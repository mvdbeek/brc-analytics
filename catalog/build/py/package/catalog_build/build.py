import pandas as pd
import yaml
import requests
import urllib
import re
import json
import time
from functools import partial
from bs4 import BeautifulSoup
import logging

MAX_NCBI_URL_LENGTH = 2000 # The actual limit seems to be a bit over 4000

log = logging.getLogger(__name__)


def rate_limit_handler(request_call):
  try:
    response = request_call()
    response.raise_for_status()
    return response
  except requests.HTTPError:
    if response.status_code == 429:
      retry_after = int(response.headers.get("Retry-After"))
      print(f"Rate limited, waiting {retry_after} seconds")
      time.sleep(retry_after)
      response = request_call()
      response.raise_for_status()
      return response
    raise

def read_assemblies(assemblies_path):
  with open(assemblies_path) as stream:
    return pd.DataFrame(yaml.safe_load(stream)["assemblies"])


def get_paginated_ncbi_results(base_url, query_description):
  page = 1
  next_page_token = None
  results = []
  while next_page_token or page == 1:
    print(f"Requesting page {page} of {query_description}")
    request_url = f"{base_url}?page_size=1000{"&page_token=" + next_page_token if next_page_token else ""}"
    response = rate_limit_handler(partial(requests.get, request_url))
    page_data = response.json()
    if len(page_data["reports"][0].get("errors", [])) > 0:
      raise Exception(page_data["reports"][0])
    results += page_data["reports"]
    next_page_token = page_data.get("next_page_token")
    page += 1
  return results


def get_next_ncbi_url_batch(get_url, items, start_index):
  # Do a binary search to find the longest possible URL
  max_valid_end_index = start_index
  min_invalid_end_index = len(items)
  end_index = len(items)
  while end_index != max_valid_end_index:
    test_url = get_url(items[start_index:end_index])
    if len(test_url) > MAX_NCBI_URL_LENGTH:
      min_invalid_end_index = end_index
    else:
      max_valid_end_index = end_index
    end_index = int((max_valid_end_index + min_invalid_end_index)/2)
  return get_url(items[start_index:end_index]), end_index


def get_batched_ncbi_urls(get_url, items):
  urls = []
  index = 0
  while index < len(items):
    url, index = get_next_ncbi_url_batch(get_url, items, index)
    urls.append(url)
  return urls


def get_batched_ncbi_results(get_base_url, items, query_description):
  results = []
  for batch_index, batch_url in enumerate(get_batched_ncbi_urls(get_base_url, items)):
    results.extend(get_paginated_ncbi_results(batch_url, f"{query_description} batch {batch_index + 1}"))
  return results


def match_taxonomic_group(tax_id, lineage, taxonomic_groups):
  if tax_id not in taxonomic_groups:
    return None
  taxon_info = taxonomic_groups[tax_id]
  name, exclude = (taxon_info["value"], taxon_info.get("exclude")) if isinstance(taxon_info, dict) else (taxon_info, None)
  if exclude is None:
    return name
  if isinstance(exclude, int):
    exclude = [exclude]
  if all(tid not in lineage for tid in exclude):
    return name
  return None


def get_taxonomic_groups(lineage, taxonomic_groups):
  return [group for group in (match_taxonomic_group(tax_id, lineage, taxonomic_groups) for tax_id in lineage) if group is not None]


def get_taxonomic_group_sets(lineage, taxonomic_group_sets):
  return {field: ",".join(get_taxonomic_groups(lineage, taxonomic_groups)) for field, taxonomic_groups in taxonomic_group_sets.items()}


def get_taxonomic_level_key(level):
  return f"taxonomicLevel{level[0].upper()}{level[1:]}"


def get_species_row(taxon_info, taxonomic_group_sets, taxonomic_levels):
  classification = taxon_info["taxonomy"]["classification"]
  species_info = classification["species"]
  taxonomy_id = taxon_info["taxonomy"]["tax_id"]
  ancestor_taxonomy_ids = taxon_info["taxonomy"]["parents"]

  taxonomic_level_fields = {get_taxonomic_level_key(level): classification.get(level, {}).get("name") for level in taxonomic_levels}
  own_level = taxon_info["taxonomy"]["rank"].lower() if "rank" in taxon_info["taxonomy"] else None
  if own_level in taxonomic_levels and own_level not in classification:
    taxonomic_level_fields[get_taxonomic_level_key(own_level)] = taxon_info["taxonomy"]["current_scientific_name"]["name"]
  
  return {
    "taxonomyId": taxonomy_id,
    "species": species_info["name"],
    "speciesTaxonomyId": species_info["id"],
    "lineageTaxonomyIds": ",".join([str(id) for id in ancestor_taxonomy_ids + [taxonomy_id]]),
    **get_taxonomic_group_sets(ancestor_taxonomy_ids, taxonomic_group_sets),
    **taxonomic_level_fields
  }


def get_species_info(taxonomy_ids):
  """
  Fetches species information from NCBI API for the given taxonomy IDs.
  
  Args:
    taxonomy_ids: List of taxonomy IDs to fetch information for
    
  Returns:
    List of species information dictionaries from NCBI
  """
  return get_batched_ncbi_results(
    lambda ids: f"https://api.ncbi.nlm.nih.gov/datasets/v2/taxonomy/taxon/{",".join(ids)}/dataset_report",
    [str(id) for id in set(taxonomy_ids)],
    "taxa"
  )


def get_species_df(species_info, taxonomic_group_sets, taxonomic_levels):
  """
  Converts species information into a DataFrame.
  
  Args:
    species_info: List of species information dictionaries from NCBI
    taxonomic_group_sets: Dictionary of taxonomic group sets
    taxonomic_levels: List of taxonomic levels to include
    
  Returns:
    DataFrame containing species information
  """
  return pd.DataFrame([get_species_row(info, taxonomic_group_sets, taxonomic_levels) for info in species_info])


def get_species_tree(taxonomy_ids, taxonomic_levels, species_info=None):
  """
  Builds a species tree from taxonomy IDs and taxonomic levels.
  
  Args:
    taxonomy_ids: List of taxonomy IDs to include in the tree
    taxonomic_levels: List of taxonomic levels to include in the tree
    species_info: Optional pre-fetched species information to avoid additional API calls
    
  Returns:
    A nested tree structure of species
  """
  species_tree_response = requests.post(
    "https://api.ncbi.nlm.nih.gov/datasets/v2/taxonomy/filtered_subtree",
    json={"taxons": [str(int(t)) for t in taxonomy_ids], "rank_limits": [t.upper() for t in taxonomic_levels]},
  ).json()

  # Build a tree from the response
  edges = species_tree_response.get("edges", {})
  all_children = {child for edge in edges.values() for child in edge.get("visible_children", [])}
  all_children = [str(num) for num in all_children]
  root_ids = [node_id for node_id in edges if node_id not in all_children]
  root_ids = [str(num) for num in root_ids]

  if not root_ids:
      return {}
  
  # this bc the ncbi result is odd, multi-root
  root_id = "1"
  for root_id_candidate in root_ids:
      if root_id_candidate != root_id:
          edges[root_id]["visible_children"].append(root_id_candidate)

  species_tree = ncbi_tree_to_nested_tree(root_id, edges, taxonomy_ids)

  # Find the set of all unique tax_ids and their display names
  tax_ids = all_children + root_ids
  tax_ids = set(tax_ids)
  
  # Initialize maps with root node
  taxon_name_map = {"1": "root"}
  taxon_rank_map = {"1": "NA"}
  
  # If we have pre-fetched species_info, use it to populate the name and rank maps
  if species_info:
    # Extract taxon names and ranks from species_info
    for info in species_info:
      tax_id = str(info["taxonomy"]["tax_id"])
      if tax_id in tax_ids:
        taxon_name_map[tax_id] = info["taxonomy"]["current_scientific_name"]["name"]
        if "rank" in info["taxonomy"]:
          taxon_rank_map[tax_id] = info["taxonomy"]["rank"]
        else:
          print(f"rank not found for tax_id: {tax_id}")
      
      # Also extract parent taxa information if available
      if "classification" in info["taxonomy"]:
        for rank_level, rank_info in info["taxonomy"]["classification"].items():
          if isinstance(rank_info, dict) and "id" in rank_info and "name" in rank_info:
            parent_name = rank_info["name"]
            parent_id = rank_info["id"]
            parent_id_str = str(parent_id)
            if parent_id_str in tax_ids and parent_id_str not in taxon_name_map:
              taxon_name_map[parent_id_str] = parent_name
              taxon_rank_map[parent_id_str] = rank_level
    
  # Fetch any missing taxa information
  fetch_taxa_info_in_batches(tax_ids, taxon_name_map, taxon_rank_map, "missing parent taxa")

  named_species_tree = update_species_tree_names(species_tree, taxon_name_map, taxon_rank_map)

  return named_species_tree


def fetch_taxa_info_in_batches(tax_ids, taxon_name_map, taxon_rank_map, description="taxa"):
  """
  Fetches taxonomic information in batches and updates the provided name and rank maps.
  
  Args:
    tax_ids: List or set of taxonomy IDs to fetch
    taxon_name_map: Dictionary to update with taxon ID to name mappings
    taxon_rank_map: Dictionary to update with taxon ID to rank mappings
    description: Description of the taxa being fetched for logging
    
  Returns:
    None (updates the provided maps in-place)
  """
  # Filter out tax_ids that are already in the map
  missing_tax_ids = [tid for tid in tax_ids if tid not in taxon_name_map and tid != "1"]
  
  if not missing_tax_ids:
    return
    
  print(f"Fetching information for {len(missing_tax_ids)} {description}")
  
  # Process in batches of 100 to avoid API limitations
  batch_size = 100
  for i in range(0, len(missing_tax_ids), batch_size):
    batch = missing_tax_ids[i:i+batch_size]
    print(f"Fetching batch {i//batch_size + 1} of {(len(missing_tax_ids) + batch_size - 1)//batch_size} ({len(batch)} taxa)")
    
    taxa_info = get_paginated_ncbi_results(
      f"https://api.ncbi.nlm.nih.gov/datasets/v2/taxonomy/taxon/{','.join(batch)}/dataset_report", 
      f"{description} batch {i//batch_size + 1}"
    )
    
    for report in taxa_info:
      tax_id = str(report["taxonomy"]["tax_id"])
      taxon_name_map[tax_id] = report["taxonomy"]["current_scientific_name"]["name"]
      if "rank" in report["taxonomy"]:
        taxon_rank_map[tax_id] = report["taxonomy"]["rank"]
      else:
        print(f"rank not found for tax_id: {tax_id}")


def ncbi_tree_to_nested_tree(node_id, edges, taxonomy_ids):
  children = edges.get(str(node_id), {}).get("visible_children", [])
  children = [str(num) for num in children]
  # ncbi results odd again, dup children
  children = set(children)
  if (len(children) > 0 or int(node_id) in taxonomy_ids):
    child_trees = [ncbi_tree_to_nested_tree(child, edges, taxonomy_ids) for child in children]
    child_trees = [item for item in child_trees if item is not None]
    return {
      "name": node_id,
      "ncbi_tax_id": node_id,
      "children": child_trees
    }

def update_species_tree_names(tree, taxon_name_map, taxon_rank_map):
    tree["rank"] = taxon_rank_map.get(tree["name"], "Unknown")
    tree["name"] = taxon_name_map.get(tree["name"], tree["name"])

    for child in tree.get("children", []):
        update_species_tree_names(child, taxon_name_map, taxon_rank_map)
    return tree

def get_genome_row(genome_info):
  refseq_category = genome_info["assembly_info"].get("refseq_category")
  return {
    "strain": genome_info["organism"].get("infraspecific_names", {}).get("strain", ""),
    "taxonomyId": genome_info["organism"]["tax_id"],
    "accession": genome_info["accession"],
    "isRef": refseq_category == "reference genome",
    "level": genome_info["assembly_info"]["assembly_level"],
    "chromosomeCount": genome_info["assembly_stats"].get("total_number_of_chromosomes"),
    "length": genome_info["assembly_stats"]["total_sequence_length"],
    "scaffoldCount": genome_info["assembly_stats"].get("number_of_scaffolds"),
    "scaffoldN50": genome_info["assembly_stats"].get("scaffold_n50"),
    "scaffoldL50": genome_info["assembly_stats"].get("scaffold_l50"),
    "coverage": genome_info["assembly_stats"].get("genome_coverage"),
    "gcPercent": genome_info["assembly_stats"].get("gc_percent"),
    "annotationStatus": genome_info.get("annotation_info", {}).get("status"),
    "pairedAccession": genome_info.get("paired_accession"),
  }


def get_biosample_data(genome_info):
  return {
    "accession": genome_info["accession"],
    "biosample": genome_info["assembly_info"]["biosample"]["accession"],
    'sample_ids': ",".join([f"{sample['db']}:{sample['value']}" for sample in genome_info["assembly_info"]["biosample"].get('sample_ids', '') if 'db' in sample]),
  }


def get_genomes_and_primarydata_df(accessions):
  genomes_info = get_batched_ncbi_results(
    lambda a: f"https://api.ncbi.nlm.nih.gov/datasets/v2/genome/accession/{",".join(a)}/dataset_report",
    accessions,
    "genomes"
  )

  return (
          pd.DataFrame(data=[get_genome_row(info) for info in genomes_info]),
          pd.DataFrame(data=[get_biosample_data(info) for info in genomes_info if 'biosample' in info['assembly_info']]))


def _id_to_gene_model_url(asm_id: str, session: requests.Session):
  print(f"finding gene model url for: {asm_id}")
  ucsc_files_endpoint = "https://genome.ucsc.edu/list/files"
  download_base_url = "https://hgdownload.soe.ucsc.edu"
  response = session.get(ucsc_files_endpoint, params={"genome": asm_id})
  try:
    response.raise_for_status()
  except Exception:
    # FIXME?: Some accessions don't have a gene folder
    return None
  # find link to gtf, should ideally be ncbiRefSeq, but augustus will do
  files = response.json()
  gtf_urls = [entry["url"] for entry in files["urlList"] if entry["url"].endswith(".gtf.gz")]
  augustus_url = None
  for url in gtf_urls:
    if "ncbiGene" in url:
      return urllib.parse.urljoin(f"{download_base_url}/", url)
    elif "ncbiRefSeq" in url:
      return urllib.parse.urljoin(f"{download_base_url}/", url)
    elif "augustus" in url:
      augustus_url = url
  if augustus_url:
    return urllib.parse.urljoin(f"{download_base_url}/", augustus_url)
  # No match, I guess that's OK ?
  return None


def add_gene_model_url(genomes_df: pd.DataFrame):
  print("Fetching gene model URLs")
  session = requests.Session()
  return pd.concat([genomes_df, genomes_df["accession"].apply(partial(_id_to_gene_model_url, session=session)).rename("geneModelUrl")], axis="columns")


def report_missing_values_from(values_name, message_predicate, all_values_series, *partial_values_series):
  present_values_mask = all_values_series.astype(bool)
  present_values_mask[:] = False
  for series in partial_values_series:
    present_values_mask |= all_values_series.isin(series)
  return report_missing_values(values_name, message_predicate, all_values_series, present_values_mask)


def report_missing_values(values_name, message_predicate, values_series, present_values_mask):
  missing_values = values_series[~present_values_mask]
  if len(missing_values) > 0:
    if len(missing_values) > len(values_series)/2:
      present_values = values_series[present_values_mask]
      print(f"Only {len(present_values)} of {len(values_series)} {values_name} {message_predicate}: {", ".join(present_values)}")
    else:
      print(f"{len(missing_values)} {values_name} not {message_predicate}: {", ".join(missing_values)}")
  return missing_values


def report_inconsistent_taxonomy_ids(df):
  inconsistent_ids_series = df.groupby(["species", "strain"]).filter(lambda g: g["taxonomyId"].nunique() > 1).groupby(["species", "strain"])["taxonomyId"].apply(set)
  inconsistent_ids_strings = [(f"{species} strain {strain}" if strain else species, ", ".join([str(id) for id in ids])) for (species, strain), ids in inconsistent_ids_series.items()]
  if len(inconsistent_ids_strings) > 0:
    print(f"Taxa with inconsistent taxonomy IDs: {", ".join([f"{taxon} ({ids})" for taxon, ids in inconsistent_ids_strings])}")
  return inconsistent_ids_strings


def fetch_sra_metadata(srs_ids, batch_size=20):
  """
  Fetches metadata for a list of SRS IDs from the SRA database.

  This function retrieves metadata for a given list of SRS (SRA Sample) IDs by querying the NCBI and EBI databases.
  It fetches the metadata in batches and handles retries and waiting mechanisms for failed requests. The metadata includes
  information about the experiment, platform, instrument, library, and associated files.

  Args:
    srs_ids (list): A list of SRS IDs to fetch metadata for.
    batch_size (int, optional): The number of SRS IDs to process in each batch. Defaults to 20.

  Returns:
    dict: A dictionary containing the fetched metadata, organized by sample accession and run accession.

  Raises:
    Exception: If the data could not be fetched after the specified number of retries or if duplicate entries are found.
  """
  def fetch_url_data(url, counter=0, counter_limit=2, wait_time=2, num_retry=3):
    """
    Fetches data from a given URL with retry and wait mechanisms.
    Args:
      url (str): The URL to fetch data from.
      counter (int, optional): The current retry counter. Defaults to 0.
      counter_limit (int, optional): The maximum number of retries before waiting. Defaults to 3.
      wait_time (int, optional): The time to wait before retrying in seconds. Defaults to 5.
      num_retry (int, optional): The number of retry attempts. Defaults to 3.
    Returns:
      tuple: A tuple containing the JSON response and the updated counter.
    Raises:
      Exception: If the data could not be fetched after the specified number of retries.
    """
    if counter > counter_limit:
      time.sleep(wait_time)
      counter = 0

    response = requests.get(url)
    while num_retry > 0 and response.status_code != 200:
      time.sleep(wait_time)
      log.debug(f"Failed to fetch, status: {response.status_code}, url: {url}. Retrying...")
      response = requests.get(url)
      num_retry -= 1

    if num_retry <= 0:
      raise Exception(f"Failed to fetch, status: {response.status_code}, url: {url} ")
    log.debug(f"Fetching data from {url}")
    return response, counter + 1

  if srs_ids is None:
    return None

  data = {}
  counter = 0
  samples_processed = 0
  for i in range(0, len(srs_ids), batch_size):
    print(f"Processing metadata for samples: {samples_processed} of {len(srs_ids)}", end='\r')
    batch_srs_id = srs_ids[i:i + batch_size]
    samples_processed += len(batch_srs_id)
    search_data, counter = fetch_url_data(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=sra&term={"+OR+".join(batch_srs_id)}&retmode=json&retmax=1000", counter)
    search_data = search_data.json()

    if int(search_data.get("esearchresult", {}).get("count", 0)) == 0:
      log.debug(f"No SRR IDs found for SRS {batch_srs_id}")
      return None

    # Extract SRR IDs
    srr_ids = search_data.get("esearchresult", {}).get("idlist", [])
    if srr_ids:
      for i in range(0, len(srr_ids), batch_size):
        batch_srr_id = srr_ids[i:i + batch_size]
        summary_data, counter = fetch_url_data(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=sra&id={','.join(batch_srr_id)}&retmode=json&retmax=1000", counter)
        summary_data = summary_data.json()
        if 'result' in summary_data:
          for result in summary_data['result']['uids']:
              exp_soup = BeautifulSoup(f"<Root>{summary_data['result'][result]['expxml']}</Root>", 'xml')
              run_soup = BeautifulSoup(f"<Root>{summary_data['result'][result]['runs']}</Root>", 'xml')

              library_layout = exp_soup.find("LIBRARY_LAYOUT").find().name
              title = exp_soup.find("Title").text
              platform = exp_soup.find("Platform").text
              instrument = exp_soup.find("Platform")["instrument_model"]
              organism_name = exp_soup.find("Organism").get("ScientificName", "")
              total_spots = exp_soup.find("Statistics")["total_spots"]
              total_bases = exp_soup.find("Statistics")["total_bases"]

              sra_experiment_acc = exp_soup.find("Experiment")["acc"]
              sra_sample_acc = exp_soup.find("Sample")["acc"]
              sra_study_acc = exp_soup.find("Study")["acc"]
              sra_submitter_acc = exp_soup.find("Submitter")["acc"]

              library_name = exp_soup.find("LIBRARY_NAME").text if exp_soup.find("LIBRARY_NAME") else ""
              library_strategy = exp_soup.find("LIBRARY_STRATEGY").text if exp_soup.find("LIBRARY_STRATEGY") else ""
              library_source = exp_soup.find("LIBRARY_SOURCE").text if exp_soup.find("LIBRARY_SOURCE") else ""
              library_selection = exp_soup.find("LIBRARY_SELECTION").text if exp_soup.find("LIBRARY_SELECTION") else ""
              bioproject_elem = exp_soup.find("Bioproject")
              bioproject = bioproject_elem.text if bioproject_elem else ""
              
              for run in run_soup.find_all("Run"):
                sra_run_acc = run["acc"]
                run_total_bases = run["total_bases"]
                run_total_spots = run["total_spots"]

                d = {
                  "title": title,
                  "platform": platform,
                  "instrument": instrument,
                  "total_spots": total_spots,
                  "total_bases": total_bases,
                  "bioproject": bioproject,
                  "organism_name": organism_name,
                  "library_name": library_name,
                  'library_layout': library_layout,
                  "library_strategy": library_strategy,
                  "library_source": library_source,
                  "library_selection": library_selection,
                  "sra_experiment_acc": sra_experiment_acc,
                  "sra_run_acc": sra_run_acc,
                  'sra_sample_acc': sra_sample_acc,
                  "sra_study_acc": sra_study_acc,
                  "sra_submitter_acc": sra_submitter_acc,
                  "run_total_bases": run_total_bases,
                  "run_total_spots": run_total_spots,
                }

                if sra_sample_acc in data:
                    if sra_run_acc in data[sra_sample_acc]:
                        raise Exception(f"Duplicate biosample run_acc {sra_run_acc} found {sra_sample_acc}")
                    else:
                        data[sra_sample_acc][sra_run_acc] = d
                else:
                    data[sra_sample_acc] = {sra_run_acc: d}
  print(f"Processing metadata for samples: {samples_processed} of {len(srs_ids)}", end='\n')
  samples_processed = 0
  for sample_acc in data:
    print(f"Adding file urls to : {samples_processed} of {len(data)}", end='\r')
    samples_processed += 1
    # Fetch url, file size and md5 for raw/primary data files
    file_list_data, counter = fetch_url_data(f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={sample_acc}&result=read_run&format=json&retmax=1000", counter)
    file_list_data = file_list_data.json()
    for result in file_list_data:
      if result['run_accession'] not in data[sample_acc]:
        raise Exception(f"Not metadata found for {result['run_accession']} {sample_acc}")
      if 'fastq_ftp' in data[sample_acc][result['run_accession']]:
        raise Exception(f"Duplicate file list entry for {result['run_accession']}  {sample_acc}")

      data[sample_acc][result['run_accession']]['file_urls'] = result['fastq_ftp']
      data[sample_acc][result['run_accession']]['file_size'] = result['fastq_bytes']
      data[sample_acc][result['run_accession']]['file_md5'] = result['fastq_md5']

      data[sample_acc][result['run_accession']]['file_urls'] = result['fastq_ftp']
      data[sample_acc][result['run_accession']]['file_size'] = result['fastq_bytes']
      data[sample_acc][result['run_accession']]['file_md5'] = result['fastq_md5']

      if not len(data[sample_acc][result['run_accession']]['file_urls']):
        # Some raw or primary data has been uploaded but not properly processed by SRA.
        # These files will lack https/ftp URLs and statistics, looks like these are
        # BAM files that are labeled as FASTQ.
        # For these, we can retrieve S3 links instead.
        file_list_data, counter = fetch_url_data(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id=SRR25741043&retmode=xml", counter)
        srafile_soup = BeautifulSoup(file_list_data.text, 'xml')
        for file in srafile_soup.findAll("SRAFile"):
          if file['supertype'] == "Original":
            alternatives = file.find('Alternatives')
            data[sample_acc][result['run_accession']]['file_urls'] = alternatives['url']
            data[sample_acc][result['run_accession']]['file_size'] = file['size']
            data[sample_acc][result['run_accession']]['file_md5'] = file['md5']
  print(f"Adding file urls to : {samples_processed} of {len(data)}", end='\n')
  return data


def make_qc_report(missing_ncbi_assemblies, inconsistent_taxonomy_ids, missing_ucsc_assemblies, missing_gene_model_urls=None):
  ncbi_assemblies_text = "None" if len(missing_ncbi_assemblies) == 0 else "\n".join([f"- {accession}" for accession in missing_ncbi_assemblies])
  ucsc_assemblies_text = "None" if len(missing_ucsc_assemblies) == 0 else "\n".join([f"- {accession}" for accession in missing_ucsc_assemblies])
  gene_model_urls_text = "N/A" if missing_gene_model_urls is None else "None" if len(missing_gene_model_urls) == 0 else "\n".join([f"- {accession}" for accession in missing_gene_model_urls])
  taxonomy_ids_text = "None" if len(inconsistent_taxonomy_ids) == 0 else "\n".join([f"- {taxon}: {ids}" for taxon, ids in inconsistent_taxonomy_ids])
  return f"# Catalog QC report\n\n## Assemblies not found on NCBI\n\n{ncbi_assemblies_text}\n\n## Assemblies not found in UCSC list\n\n{ucsc_assemblies_text}\n\n## Assemblies with gene model URLs not found\n\n{gene_model_urls_text}\n\n## Species and strain combinations with multiple taxonomy IDs\n\n{taxonomy_ids_text}\n"


def build_files(
  assemblies_path,
  genomes_output_path,
  ucsc_assemblies_url,
  tree_output_path,
  taxonomic_levels_for_tree, 
  taxonomic_group_sets={},
  do_gene_model_urls=True,
  extract_primary_data=False,
  primary_output_path=None,
  qc_report_path=None
):
  print("Building files")

  qc_report_params = {}

  source_list_df = read_assemblies(assemblies_path)

  base_genomes_df, primarydata_df = get_genomes_and_primarydata_df(source_list_df["accession"])

  primarydata_df['sra_sample_acc'] = primarydata_df["sample_ids"].str.split(",")
  primarydata_df = primarydata_df.explode("sra_sample_acc")
  primarydata_df = primarydata_df[~primarydata_df["sra_sample_acc"].isnull() & primarydata_df["sra_sample_acc"].str.startswith('SRA')]
  primarydata_df["sra_sample_acc"] = primarydata_df["sra_sample_acc"].str.replace("SRA:", "")
  if extract_primary_data:
    sra_ids_list = primarydata_df["sra_sample_acc"].dropna().unique().tolist()
    sra_metadata = fetch_sra_metadata(sra_ids_list)
    sra_metadata_df = pd.DataFrame([sra_metadata[sra][srr] for sra in sra_metadata for srr in sra_metadata[sra]])
    primarydata_df = primarydata_df.merge(sra_metadata_df, how="left", left_on="sra_sample_acc", right_on="sra_sample_acc")
  
  qc_report_params["missing_ncbi_assemblies"] = report_missing_values_from("accessions", "found on NCBI", source_list_df["accession"], base_genomes_df["accession"])

  # Fetch species information once to be used by both species_df and species_tree
  species_info = get_species_info(base_genomes_df["taxonomyId"])
  
  # Create species DataFrame using the fetched species_info
  species_df = get_species_df(species_info, taxonomic_group_sets, taxonomic_levels_for_tree)

  report_missing_values_from("species", "found on NCBI", base_genomes_df["taxonomyId"], species_df["taxonomyId"])

  genomes_with_species_df = base_genomes_df.merge(species_df, how="left", on="taxonomyId")

  qc_report_params["inconsistent_taxonomy_ids"] = report_inconsistent_taxonomy_ids(genomes_with_species_df)

  assemblies_df = pd.DataFrame(requests.get(ucsc_assemblies_url).json()["data"])[["ucscBrowser", "genBank", "refSeq"]]

  gen_bank_merge_df = genomes_with_species_df.merge(assemblies_df, how="left", left_on="accession", right_on="genBank")
  ref_seq_merge_df = genomes_with_species_df.merge(assemblies_df, how="left", left_on="accession", right_on="refSeq")

  qc_report_params["missing_ucsc_assemblies"] = report_missing_values_from("accessions", "matched in assembly list", genomes_with_species_df["accession"], assemblies_df["genBank"], assemblies_df["refSeq"])

  genomes_df = gen_bank_merge_df.combine_first(ref_seq_merge_df)

  if do_gene_model_urls:
    genomes_df = add_gene_model_url(genomes_df)
    qc_report_params["missing_gene_model_urls"] = report_missing_values("accessions", "matched with gene model URLs", genomes_df["accession"], genomes_df["geneModelUrl"].astype(bool))
  else:
    genomes_df["geneModelUrl"] = ""

  genomes_df.to_csv(genomes_output_path, index=False, sep="\t")

  print(f"Wrote to {genomes_output_path}")

  if extract_primary_data:
    primarydata_df.to_csv(primary_output_path, index=False, sep="\t")
    print(f"Wrote to {primary_output_path}")
  
  if qc_report_path is not None:
    qc_report_text = make_qc_report(**qc_report_params)
    with open(qc_report_path, "w") as file:
      file.write(qc_report_text)

  if len(taxonomic_levels_for_tree) > 0:
    # Use the taxonomy IDs from the genomes_df to build the species tree
    # Pass the previously fetched species_info to avoid another API call
    species_tree = get_species_tree(list(genomes_df["taxonomyId"]), taxonomic_levels_for_tree, species_info)
    with open(tree_output_path, 'w') as outfile:
      json.dump(species_tree, outfile, indent=4)
    print(f"Wrote to {tree_output_path}")
  
