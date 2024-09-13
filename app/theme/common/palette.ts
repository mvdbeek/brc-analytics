import { PaletteColor } from "@mui/material";

/**
 * Palette "Hero"
 */
enum HERO {
  LIGHT = "#28285B",
  MAIN = "#28285B",
}

/**
 * Color constants
 */
export const heroLight = HERO.LIGHT;
export const heroMain = HERO.MAIN;

/**
 * Palette Option "Hero"
 */
export const hero: PaletteColor = {
  contrastText: "#FFFFFF",
  dark: heroMain,
  light: heroLight,
  main: heroMain,
};
