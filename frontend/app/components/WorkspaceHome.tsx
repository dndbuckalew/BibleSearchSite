import Link from "next/link";

export default function WorkspaceHome() {
  return (
    <div className="mb-4 flex justify-end">
      <Link
        href="/"
        className="bta-button"
      >
        Home
      </Link>
    </div>
  );
}
