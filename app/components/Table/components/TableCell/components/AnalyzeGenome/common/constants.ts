import { CustomSVGIconProps } from "@databiosphere/findable-ui/lib/components/common/CustomIcon/common/entities";
import {
  ButtonProps,
  ButtonGroupProps as MButtonGroupProps,
} from "@mui/material";

export const BUTTON_PROPS: Partial<ButtonProps> = {
  color: "secondary",
  variant: "contained",
};

export const BUTTON_GROUP_PROPS: Partial<MButtonGroupProps> = {
  color: "secondary",
  variant: "outlined",
};

export const ICON_PROPS: Partial<CustomSVGIconProps> = {
  color: "inkLight",
  fontSize: "small",
};
