import { AboutContent } from "../../../../content";
import { Section } from "../../section.styles";
import { StyledSectionLayout } from "./sectionAbout.styles";

export const SectionAbout = (): JSX.Element => {
  return (
    <Section>
      <StyledSectionLayout>
        <AboutContent />
      </StyledSectionLayout>
    </Section>
  );
};
