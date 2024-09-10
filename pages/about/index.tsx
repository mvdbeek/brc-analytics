import { GetStaticProps } from "next";
import { StyledPagesMain } from "../../app/components/Layout/components/Main/main.styles";
import { AboutView } from "../../app/views/AboutView/aboutView";

export const About = (): JSX.Element => {
  return <AboutView />;
};

export const getStaticProps: GetStaticProps = async () => {
  return {
    props: {
      pageTitle: "About",
    },
  };
};

export default About;

About.Main = StyledPagesMain;