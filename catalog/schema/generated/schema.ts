/**
* Possible ploidies of an organism.
*/
export enum OrganismPloidy {
    
    DIPLOID = "DIPLOID",
    HAPLOID = "HAPLOID",
    POLYPLOID = "POLYPLOID",
};
/**
* Set of IDs of workflow categories.
*/
export enum WorkflowCategoryId {
    
    VARIANT_CALLING = "VARIANT_CALLING",
    TRANSCRIPTOMICS = "TRANSCRIPTOMICS",
    REGULATION = "REGULATION",
    ASSEMBLY = "ASSEMBLY",
    GENOME_COMPARISONS = "GENOME_COMPARISONS",
    PROTEIN_FOLDING = "PROTEIN_FOLDING",
    OTHER = "OTHER",
};
/**
* Possible ploidies supported by workflows.
*/
export enum WorkflowPloidy {
    
    ANY = "ANY",
    DIPLOID = "DIPLOID",
    HAPLOID = "HAPLOID",
    POLYPLOID = "POLYPLOID",
};


/**
 * Object containing list of assemblies.
 */
export interface Assemblies {
    /** List of assemblies. */
    assemblies: Assembly[],
}


/**
 * An assembly.
 */
export interface Assembly {
    /** The assembly's accession. */
    accession: string,
}


/**
 * Object containing list of organisms.
 */
export interface Organisms {
    /** List of organisms. */
    organisms: Organism[],
}


/**
 * Info for an organism.
 */
export interface Organism {
    /** The organism's NCBI taxonomy ID. */
    taxonomy_id: number,
    /** The ploidies that the organism may have. */
    ploidy: OrganismPloidy[],
}


/**
 * Object containing list of workflow categories.
 */
export interface WorkflowCategories {
    /** List of workflow categories. */
    workflow_categories: WorkflowCategory[],
}


/**
 * Workflow category.
 */
export interface WorkflowCategory {
    /** The ID of the workflow category. */
    category: WorkflowCategoryId,
    /** The display name of the workflow category. */
    name: string,
    /** The description of the workflow category. */
    description: string,
}


/**
 * Object containing list of workflows.
 */
export interface Workflows {
    /** List of workflows. */
    workflows: Workflow[],
}


/**
 * A workflow.
 */
export interface Workflow {
    /** The workflow's TRS ID. */
    trs_id: string,
    /** The IDs of the categories the workflow belongs to. */
    categories: WorkflowCategoryId[],
    /** The ploidy supported by the workflow. */
    ploidy: WorkflowPloidy,
    /** The NCBI ID of the taxon supported by the workflow. */
    taxonomy_id?: number | null,
    /** The display name of the workflow. */
    workflow_name: string,
    /** The description of the workflow. */
    workflow_description: string,
    /** The parameters of the workflow. Dictionary with arbitrary depth, string keys and primitive values. */
    parameters?: Record<string, any>,
    /** Determines if workflow should be included. */
    active: boolean,
}



