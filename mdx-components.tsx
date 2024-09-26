import { Link } from "@databiosphere/findable-ui/lib/components/Links/components/Link/link";
import { MDXComponents } from "mdx/types";
import { CardActions } from "./app/components/Home/components/Section/components/SectionHero/components/Carousel/components/Cards/cards.styles";

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    ...components,
    CardActions,
    Link,
    a: ({ children, href }) => Link({ label: children, url: href ?? "" }),
  };
}
