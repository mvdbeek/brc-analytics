import { createTheme, Theme } from "@mui/material";
import { deepmerge } from "@mui/utils";
import * as C from "./common/components";
import * as P from "./common/palette";

/**
 * Returns BRC customized theme.
 * @param theme -- Base theme
 * @returns theme with custom theme overrides.
 */
export function mergeAppTheme(theme: Theme): Theme {
  const appTheme = { ...theme };

  // Merge palette with hero color.
  appTheme.palette = { ...appTheme.palette, hero: P.hero };

  // Marge custom components.
  const components = {
    MuiButton: C.MuiButton(appTheme),
    MuiCssBaseline: C.MuiCssBaseline(appTheme),
  };

  return createTheme(deepmerge(appTheme, components));
}
