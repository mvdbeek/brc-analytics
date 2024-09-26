import {
  getBorderBoxSizeHeight,
  useResizeObserver,
} from "@databiosphere/findable-ui/lib/hooks/useResizeObserver";
import { useRef } from "react";
import { StyledSection } from "./section.styles";

export interface SectionProps {
  children: (height?: number) => JSX.Element;
  className?: string;
}

export const Section = ({ children, className }: SectionProps): JSX.Element => {
  const sectionRef = useRef<HTMLElement>(null);
  const { height } =
    useResizeObserver(sectionRef, getBorderBoxSizeHeight) || {};
  return (
    <StyledSection className={className} ref={sectionRef}>
      {children?.(height)}
    </StyledSection>
  );
};
