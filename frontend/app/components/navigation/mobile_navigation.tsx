import Link from "next/link";
import { primaryNavigation } from "../../platform/navigation/navigation_configuration";

export default function MobileNavigation() {
  return (
    <nav
      aria-label="Mobile Navigation"
      className="w-full border-t border-gray-200 bg-white"
    >
      <div className="flex flex-col items-center py-3 gap-3">
        {primaryNavigation
          .filter((item) => item.display !== false)
          .map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-neutral-700 hover:text-blue-600 transition-colors text-lg"
            >
              {item.label}
            </Link>
          ))}
      </div>
    </nav>
  );
}
