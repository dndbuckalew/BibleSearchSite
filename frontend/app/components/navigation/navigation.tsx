import Link from "next/link";

export default function Navigation() {
  return (
    <nav
      aria-label="Primary Navigation"
      className="text-xl font-normal"
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        gap: "20px",
        marginTop: "16px",
      }}
    >
      <Link
        href="/"
        className="text-neutral-700 hover:text-blue-600 transition-colors"
      >
        Home
      </Link>

      <Link
        href="/stay-connected"
        className="text-neutral-700 hover:text-blue-600 transition-colors"
        style={{ marginRight: "32px", textAlign: "center" }}
      >
        <span
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            lineHeight: "1.0",
          }}
        >
          <span>Stay</span>
          <span>Connected</span>
        </span>
      </Link>

      <Link
        href="/donation"
        className="text-neutral-700 hover:text-blue-600 transition-colors"
        style={{ marginRight: "32px" }}
      >
        Donate
      </Link>

      <Link
        href="/about"
        className="text-neutral-700 hover:text-blue-600 transition-colors"
        style={{ marginRight: "32px", textAlign: "center" }}
      >
        <span
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            lineHeight: "1.0",
          }}
        >
          <span>About</span>
          <span>Us</span>
        </span>
      </Link>
    </nav>
  );
}
