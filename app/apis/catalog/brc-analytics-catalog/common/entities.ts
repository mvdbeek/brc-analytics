import { ORGANISM_PLOIDY, WORKFLOW_PLOIDY } from "./schema-entities";

export type BRCCatalog = BRCDataCatalogGenome;

export interface BRCDataCatalogGenome {
  accession: string;
  annotationStatus: string | null;
  chromosomes: number | null;
  coverage: string | null;
  gcPercent: number | null;
  geneModelUrl: string | null;
  isRef: string;
  length: number;
  level: string;
  lineageTaxonomyIds: string[];
  ncbiTaxonomyId: string;
  ploidy: ORGANISM_PLOIDY[];
  scaffoldCount: number | null;
  scaffoldL50: number | null;
  scaffoldN50: number | null;
  speciesTaxonomyId: string;
  strainName: string | null;
  taxonomicGroup: string[];
  taxonomicLevelClass: string;
  taxonomicLevelFamily: string;
  taxonomicLevelGenus: string;
  taxonomicLevelKingdom: string;
  taxonomicLevelOrder: string;
  taxonomicLevelPhylum: string;
  taxonomicLevelSpecies: string;
  taxonomicLevelStrain: string;
  taxonomicLevelSuperkingdom: string;
  ucscBrowserUrl: string | null;
}

export interface BRCDataCatalogOrganism {
  assemblyCount: number;
  assemblyTaxonomyIds: string[];
  genomes: BRCDataCatalogGenome[];
  ncbiTaxonomyId: string;
  taxonomicGroup: string[];
  taxonomicLevelClass: string;
  taxonomicLevelFamily: string;
  taxonomicLevelGenus: string;
  taxonomicLevelKingdom: string;
  taxonomicLevelOrder: string;
  taxonomicLevelPhylum: string;
  taxonomicLevelSpecies: string;
  taxonomicLevelStrain: string[];
  taxonomicLevelSuperkingdom: string;
}

export interface EntitiesResponse<R> {
  hits: R[];
  pagination: EntitiesResponsePagination;
  termFacets: Record<never, never>;
}

export interface EntitiesResponsePagination {
  count: number;
  pages: number;
  size: number;
  total: number;
}

export interface WorkflowCategory {
  category: string;
  description: string;
  name: string;
  workflows: Workflow[];
}

export interface Workflow {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- True type is something like { [key: string]: string | string[] }, but can't model with linkml
  parameters: any;
  ploidy: WORKFLOW_PLOIDY;
  taxonomyId: string | null;
  trsId: string;
  workflowDescription: string;
  workflowName: string;
}
