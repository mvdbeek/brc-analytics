import { GetStaticProps } from "next";
import { StyledPagesMain } from "../../app/components/Layout/components/Main/main.styles";
import { RoadmapView } from "../../app/views/RoadmapView/roadmapView";

export const Roadmap = (): JSX.Element => {
  return <RoadmapView />;
};

export const getStaticProps: GetStaticProps = async () => {
  return {
    props: {
      pageTitle: "Roadmap",
    },
  };
};

export default Roadmap;

Roadmap.Main = StyledPagesMain;