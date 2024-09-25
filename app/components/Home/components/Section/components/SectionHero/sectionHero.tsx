import { Button } from "@mui/material";
import { ROUTES } from "../../../../../../../routes/constants";
import { Carousel } from "./components/Carousel/carousel";
import { Hero } from "./components/Hero/hero";
import {
  Head,
  Headline,
  Section,
  SectionLayout,
  Subhead,
  SubHeadline,
} from "./sectionHero.styles";

export const SectionHero = (): JSX.Element => {
  return (
    <Section>
      <Hero gridSize={228} />
      <SectionLayout>
        <Headline>
          <Head>
            <span>Analytics for pathogen, </span>
            <span>host, and vector data</span>
          </Head>
          <SubHeadline>
            <Subhead>
              Comprehensive tools for exploring and interpreting genomic
              annotations and functional insights into disease-causing organisms
              and their carriers
            </Subhead>
            <Button color="hero" href={ROUTES.ORGANISMS} variant="contained">
              Get started
            </Button>
          </SubHeadline>
        </Headline>
        <Carousel />
      </SectionLayout>
    </Section>
  );
};
