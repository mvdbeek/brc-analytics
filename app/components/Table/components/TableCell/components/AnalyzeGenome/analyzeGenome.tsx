import {
  ANCHOR_TARGET,
  REL_ATTRIBUTE,
} from "@databiosphere/findable-ui/lib/components/Links/common/entities";
import { Button, Tooltip } from "@mui/material";
import Router from "next/router";
import { ROUTES } from "../../../../../../../routes/constants";
import { AnalyzeGenomeIcon } from "../../../../../common/CustomIcon/components/AnalyzeGenomeIcon/analyzeGenomeIcon";
import { ViewGenomeIcon } from "../../../../../common/CustomIcon/components/ViewGenomeIcon/viewGenomeIcon";
import { StyledButtonGroup } from "./analyzeGenome.styles";
import {
  BUTTON_GROUP_PROPS,
  BUTTON_PROPS,
  ICON_PROPS,
} from "./common/constants";

export interface AnalyzeGenomeProps {
  genomeVersionAssemblyId: string;
  rowId?: string;
  ucscBrowserUrl: string;
}

export const AnalyzeGenome = ({
  genomeVersionAssemblyId,
  rowId,
  ucscBrowserUrl,
}: AnalyzeGenomeProps): JSX.Element => {
  const onAnalyze = (rowId?: string): void => {
    if (!rowId) return;
    Router.push(`${ROUTES.ORGANISMS}/${rowId}`);
  };

  const onView = (url: string | null): void => {
    if (!url) return;
    window.open(url, ANCHOR_TARGET.BLANK, REL_ATTRIBUTE.NO_OPENER_NO_REFERRER);
  };

  return (
    <StyledButtonGroup
      {...BUTTON_GROUP_PROPS}
      Buttons={[
        <Tooltip key="analyze" title="Analyze">
          <Button
            {...BUTTON_PROPS}
            disabled={!rowId}
            onClick={(): void => onAnalyze(rowId)}
          >
            <AnalyzeGenomeIcon {...ICON_PROPS} />
          </Button>
        </Tooltip>,
        <Tooltip key="view-browser" title="UCSC Genome Browser">
          <Button
            {...BUTTON_PROPS}
            disabled={!ucscBrowserUrl}
            onClick={(): void => onView(ucscBrowserUrl)}
          >
            <ViewGenomeIcon {...ICON_PROPS} />
          </Button>
        </Tooltip>,
        <Tooltip key="view-datasets" title="NCBI datasets">
          <Button
            {...BUTTON_PROPS}
            disabled={!genomeVersionAssemblyId}
            onClick={(): void =>
              onView(
                `https://www.ncbi.nlm.nih.gov/datasets/genome/${genomeVersionAssemblyId}`
              )
            }
          >
            NCBI
          </Button>
        </Tooltip>,
      ]}
    />
  );
};
