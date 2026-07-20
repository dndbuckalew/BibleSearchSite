import Link from "next/link";

export default function MenuPage() {
  return (
    <main
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "2rem 1.5rem",
      }}
    >
      <h1
        style={{
          fontSize: "2rem",
          marginBottom: "0.5rem",
        }}
      >
        Menu
      </h1>

      <p
        style={{
          color: "#666",
          marginBottom: "2rem",
        }}
      >
        Explore Bible Therapy Assistant™ resources and platform information.
      </p>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Platform</h2>

        <ul style={{ listStyle: "none", padding: 0 }}>
          <li style={{ margin: "0.75rem 0" }}>
            <Link href="/menu/how_bta_works">
              How BTA Works
            </Link>
          </li>
        </ul>
      </section>

      <section style={{ marginBottom: "2rem" }}>
        <h2>Platform Status</h2>

        <ul style={{ listStyle: "none", padding: 0 }}>
          <li>What's New (Coming Soon)</li>
          <li>Release Notes (Coming Soon)</li>
          <li>Version Information (Coming Soon)</li>
        </ul>
      </section>

      <section>
        <h2>Communication</h2>

        <ul style={{ listStyle: "none", padding: 0 }}>
          <li>Contact (Coming Soon)</li>
          <li>Feedback (Coming Soon)</li>
        </ul>
      </section>
    </main>
  );
}
