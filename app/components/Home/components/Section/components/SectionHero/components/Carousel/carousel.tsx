import {
  Carousel as CarouselCards,
  CarouselView,
  StyledBullets,
} from "./carousel.styles";
import { Cards } from "./components/Cards/cards";
import { useInteractiveCarousel } from "./hooks/useInteractiveCarousel";

export const Carousel = (): JSX.Element => {
  const {
    activeIndex,
    interactiveAction,
    interactiveCards,
    interactiveIndexes,
    onSetActiveIndex,
  } = useInteractiveCarousel();
  return (
    <CarouselView>
      <CarouselCards {...interactiveAction}>
        <Cards activeIndex={activeIndex} cards={interactiveCards} />
        <StyledBullets
          activeBullet={activeIndex}
          bullets={interactiveIndexes}
          onBullet={onSetActiveIndex}
        />
      </CarouselCards>
    </CarouselView>
  );
};
