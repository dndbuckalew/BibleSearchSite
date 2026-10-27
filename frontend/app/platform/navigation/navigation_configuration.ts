import { DONATIONS_ENABLED } from "../capabilities";
import type { NavigationItem } from "./navigation_types";

export const primaryNavigation: NavigationItem[] = [
  {
    label: "Home",
    href: "/",
    display: true,
  },
  {
    label: "Stay Connected",
    href: "/stay-connected",
    display: true,
  },
  {
    label: "Donate",
    href: "/donation",
    display: DONATIONS_ENABLED,
  },
  {
    label: "About Us",
    href: "/about",
    display: true,
  },
];

export const supportingDocumentsNavigation: NavigationItem[] = [
  { label: "How BTA Works", href: "/menu/how_bta_works", display: true },
];
