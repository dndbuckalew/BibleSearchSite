import Link from "next/link";
import { primaryNavigation } from "../../platform/navigation/navigation_configuration";

export default function DesktopNavigation() {
  return (
    <nav
      aria-label="Primary Navigation"
      className="flex text-xl font-normal"
      style={{
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        gap: "0.5rem clamp(0.5rem, 2vw, 2rem)",
        marginTop: "16px",
      }}
    >
      {primaryNavigation
        .filter((item) => item.display !== false)
        .map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="min-h-11 content-center rounded px-2 py-2 text-neutral-700 hover:text-blue-600 transition-colors"
            style={{
              textAlign: "center",
            }}
          >
            {item.label}
          </Link>
        ))}
    </nav>
  );
}
