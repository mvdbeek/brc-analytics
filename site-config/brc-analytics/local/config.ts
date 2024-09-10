import { SiteConfig } from "@databiosphere/findable-ui/lib/config/entities";
import { EntityConfig } from "@databiosphere/findable-ui/src/config/entities";
import { BRCDataCatalogGenome } from "../../../app/apis/catalog/brc-analytics-catalog/common/entities";
import * as C from "../../../app/components";
import * as P from "../../../app/theme/common/palette";
import { ROUTES } from "../../../routes/constants";
import { genomeEntityConfig } from "./index/genomeEntityConfig";

const LOCALHOST = "http://localhost:3000";
const APP_TITLE = "BRC Analytics";
const BROWSER_URL = LOCALHOST;

/**
 * Make site config object.
 * @param browserUrl - Browser URL.
 *
 * @remarks
 * The `genomeEntityConfig` is typecast to `EntityConfig<BRCDataCatalogGenome>`
 * because the `SiteConfig` interface from the `@databiosphere/findable-ui` package expects
 * an array of entities typed as `EntityConfig`, but we have modified the EntityConfig
 * locally with a custom `BRCEntityConfig` entity. To avoid rewriting
 * the associated functions and providers across the codebase due to this modification,
 * we perform a type cast here. This allows us to retain compatibility with the existing
 * `SiteConfig` structure while accommodating the modified entity configuration.
 *
 * @returns site config.
 */
export function makeConfig(browserUrl: string): SiteConfig {
  return {
    appTitle: APP_TITLE,
    browserURL: browserUrl,
    dataSource: {
      url: "",
    },
    entities: [genomeEntityConfig as EntityConfig<BRCDataCatalogGenome>],
    explorerTitle: APP_TITLE,
    layout: {
      footer: {
        Branding: C.Branding(),
      },
      header: {
        logo: C.Logo({
          alt: APP_TITLE,
          height: 26,
          link: "/",
          src: "/logo/brc.svg",
        }),
        navigation: [
          undefined,
          [
            { label: "Roadmap", url: ROUTES.ROADMAP },
            { label: "Datasets", url: ROUTES.ORGANISMS },
            { label: "About", url: ROUTES.ABOUT },
          ],
          undefined,
        ],
      },
    },
    redirectRootToPath: "/",
    themeOptions: {
      palette: {
        hero: P.hero,
      },
    },
  };
}

const config: SiteConfig = makeConfig(BROWSER_URL);

export default config;
