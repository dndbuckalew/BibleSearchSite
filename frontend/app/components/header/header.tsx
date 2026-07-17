import Image from "next/image";

export default function Header() {
  return (
    <header
      style={{
        textAlign: "center",
        paddingTop: "24px",
        paddingBottom: "16px",
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
        className="mt-2 text-3xl font-medium text-neutral-900"
      >
        Bible Therapy Assistant™
      </h1>
    </header>
  );
}
