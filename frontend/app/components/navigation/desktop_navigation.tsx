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
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        gap: "32px",
        marginTop: "16px",
      }}
    >
      {primaryNavigation
        .filter((item) => item.display !== false)
        .map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="text-neutral-700 hover:text-blue-600 transition-colors"
            style={{
              textAlign: "center",
            }}
          >
            {item.label === "Stay Connected" ? (
              <>
                <span style={{ display: "block", lineHeight: "1.0" }}>
                  Stay
                </span>
                <span style={{ display: "block", lineHeight: "1.0" }}>
                  Connected
                </span>
              </>
            ) : item.label === "About Us" ? (
              <>
                <span style={{ display: "block", lineHeight: "1.0" }}>
                  About
                </span>
                <span style={{ display: "block", lineHeight: "1.0" }}>
                  Us
                </span>
              </>
            ) : (
              item.label
            )}
          </Link>
        ))}
    </nav>
  );
}
