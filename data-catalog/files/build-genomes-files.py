import pandas as pd
import re
import requests

GENOMES_SOURCE_URL = "https://docs.google.com/spreadsheets/d/1NRfTvebPl6zJ0l9tCqBtq6YCrwV6_XDBlheq3L5HcvQ/gviz/tq?tqx=out:csv&sheet=GenomeDataTypes_Summary.csv"
ASSEMBLIES_URL = "https://hgdownload.soe.ucsc.edu/hubs/BRC/assembly.list.json"

OUTPUT_PATH = "files/source/genomes.tsv"

def build_genomes_files():
  print("Building files")

  genomes_source_df = pd.read_csv(GENOMES_SOURCE_URL, keep_default_na=False, usecols=lambda name: re.fullmatch(r"Unnamed: \d+", name) is None)
  assemblies_df = pd.DataFrame(requests.get(ASSEMBLIES_URL).json()["data"])
  
  gen_bank_merge_df = genomes_source_df.merge(assemblies_df, how="left", left_on="Genome Version/Assembly ID", right_on="genBank")
  ref_seq_merge_df = genomes_source_df.merge(assemblies_df, how="left", left_on="Genome Version/Assembly ID", right_on="refSeq")

  result_df = gen_bank_merge_df.combine_first(ref_seq_merge_df)

  result_df.to_csv(OUTPUT_PATH, index=False, sep="\t")

  print(f"Wrote to {OUTPUT_PATH}")

if __name__ == "__main__":
  build_genomes_files()
