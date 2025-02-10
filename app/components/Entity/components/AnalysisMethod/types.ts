import { ReactNode } from "react";

export interface Props {
  content: ReactNode;
  geneModelUrl: string | null;
  genomeVersionAssemblyId: string;
  workflowId: string;
}
