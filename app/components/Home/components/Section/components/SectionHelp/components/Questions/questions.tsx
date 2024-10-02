import { AddIcon as DXAddIcon } from "@databiosphere/findable-ui/lib/components/common/CustomIcon/components/AddIcon/addIcon";
import { RoundedPaper as DXRoundedPaper } from "@databiosphere/findable-ui/lib/components/common/Paper/paper.styles";
import { Link as DXLink } from "@databiosphere/findable-ui/lib/components/Links/components/Link/link";
import {
  AccordionDetails as MAccordionDetails,
  AccordionSummary as MAccordionSummary,
} from "@mui/material";
import { URLS } from "../../../../../../common/constants";
import { Grid, StyledAccordion } from "./questions.styles";

export const Questions = (): JSX.Element => {
  const expandIcon = <DXAddIcon color="inkLight" fontSize="small" />;
  return (
    <Grid>
      <StyledAccordion component={DXRoundedPaper}>
        <MAccordionSummary expandIcon={expandIcon}>
          What is the plan?
        </MAccordionSummary>
        <MAccordionDetails>
          BRC Analytics is very new. Out plan is (1) establish access to
          official versions of VEuPathDB’s 785 genomes; (2) develop analytical
          workflows for common analyses such as transcriptomics, variation,
          assembly, and tightly integrate them with the data; (3) ingest and
          provide access to custom annotations that were previously available
          from VEuPathDB. To learn more click “Roadmap” on top.
        </MAccordionDetails>
      </StyledAccordion>
      <StyledAccordion component={DXRoundedPaper}>
        <MAccordionSummary expandIcon={expandIcon}>
          Where is the data?
        </MAccordionSummary>
        <MAccordionDetails>
          I used to be able to access many types of data including genomes and
          associated annotations. Where do I find it now? Data for the majority
          of VEuPathDB organisms is available by clicking the “Datasets” link at
          the top.
        </MAccordionDetails>
      </StyledAccordion>
      <StyledAccordion component={DXRoundedPaper}>
        <MAccordionSummary expandIcon={expandIcon}>
          How do I do analyses?
        </MAccordionSummary>
        <MAccordionDetails>
          I used to rely on VEuPathDB to perform my analyses. Now that it is no
          longer available, what can I do? Many types of analyses are possible
          via integration with the{" "}
          <DXLink label="Galaxy system" url={URLS.GALAXY_SYSTEM} /> while we
          continue to build this new BRC resource.
        </MAccordionDetails>
      </StyledAccordion>
      <StyledAccordion component={DXRoundedPaper}>
        <MAccordionSummary expandIcon={expandIcon}>
          How does BRC Analytics work?
        </MAccordionSummary>
        <MAccordionDetails>
          BRC Analytics will provide access to genomic data and an analytical
          environment. The data will be based on the official releases provided
          by NCBI Datasets and deployed through the UCSC Genome Browser. The
          analytics will be provided by the Galaxy system supported by powerful
          computational infrastructure provided by the Texas Advanced Computing
          Center (<DXLink label="TACC" url={URLS.TACC} />) and{" "}
          <DXLink label="ACCESS-CI" url={URLS.ACCESS_CONSORTIUM} /> consortium.
        </MAccordionDetails>
      </StyledAccordion>
    </Grid>
  );
};
