import { CardProps } from "@databiosphere/findable-ui/lib/components/common/Card/card";
import * as MDX from "../content";

export const CAROUSEL_CARDS: Pick<CardProps, "text">[] = [
  {
    text: MDX.ShareUsageAndJoinAdvisoryPanel({}),
  },
  {
    text: MDX.LearnToAnalyzeData({}),
  },
];
