import Image from "next/image";

export default function Header() {
  return (
    <header
      style={{
        textAlign: "center",
        paddingTop: "clamp(16px, 3vw, 24px)",
        paddingBottom: "clamp(12px, 2vw, 16px)",
      }}
    >
      <Image
        src="/bta/images/bta-logo.png"
        alt="Bible Therapy Assistant Logo"
        width={120}
        height={120}
        priority
        style={{
          margin: "0 auto",
        }}
      />

      <h1
        style={{
          marginTop: "12px",
          fontSize: "2rem",        // 32px
          fontWeight: 500,
          color: "#171717",
          lineHeight: 1.2,
        }}
      >
        Bible Therapy Assistant™
      </h1>
    </header>
  );
}
