import { SubHeroContent } from "../../../../content";
import { Section, SectionLayout, Subhead } from "./sectionSubHero.styles";

export const SectionSubHero = (): JSX.Element => {
  return (
    <Section>
      <SectionLayout>
        <Subhead>
          <SubHeroContent />
        </Subhead>
      </SectionLayout>
    </Section>
  );
};
