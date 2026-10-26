import Image from "next/image";

export default function Header() {
  return (
    <div className="flex min-w-0 items-center gap-3">
      <Image
        src="/bta/images/bta-logo.png"
        alt="Bible Therapy Assistant Logo"
        width={64}
        height={64}
        priority
        className="h-12 w-12 shrink-0 sm:h-16 sm:w-16"
      />

      <h1
        style={{
          minWidth: 0,
          fontSize: "clamp(1.125rem, 0.95rem + 1vw, 1.75rem)",
          fontWeight: 500,
          color: "#171717",
          lineHeight: 1.2,
        }}
      >
        Bible Therapy Assistant™
      </h1>
    </div>
  );
}
