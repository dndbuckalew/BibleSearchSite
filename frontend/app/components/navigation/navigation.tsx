"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import {
  primaryNavigation,
  supportingDocumentsNavigation,
} from "../../platform/navigation/navigation_configuration";

export default function Navigation() {
  const pathname = usePathname();
  // Reset navigation on route changes without changing the shared page shell.
  return <NavigationDisclosure key={pathname} />;
}

function NavigationDisclosure() {
  const [isOpen, setIsOpen] = useState(false);
  const [documentsOpen, setDocumentsOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelId = useId();
  const documentsId = useId();

  function closeNavigation() {
    setIsOpen(false);
    setDocumentsOpen(false);
    triggerRef.current?.focus();
  }

  // History navigation can keep the same pathname while changing results.
  useEffect(() => {
    function handleHistoryChange() {
      setIsOpen(false);
      setDocumentsOpen(false);
    }
    window.addEventListener("popstate", handleHistoryChange);
    return () => window.removeEventListener("popstate", handleHistoryChange);
  }, []);

  const controlClassName =
    "flex min-h-11 min-w-11 items-center gap-3 rounded px-3 py-2 text-left text-base text-neutral-700 hover:text-blue-600 focus-visible:outline-2 focus-visible:outline-offset-3 focus-visible:outline-blue-600";

  return (
    <nav
      aria-label="Primary Navigation"
      className="contents"
      onKeyDown={(event) => {
        if (event.key === "Escape" && isOpen) {
          event.preventDefault();
          closeNavigation();
        }
      }}
    >
      <button
        ref={triggerRef}
        type="button"
        aria-expanded={isOpen}
        aria-controls={panelId}
        className={`${controlClassName} col-start-2 row-start-1 w-11 justify-center justify-self-end px-0`}
        onClick={() => {
          if (isOpen) closeNavigation();
          else setIsOpen(true);
        }}
      >
        <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" strokeWidth="2" className="shrink-0">
          <path d={isOpen ? "M6 6l12 12M6 18L18 6" : "M3 6h18M3 12h18M3 18h18"} />
        </svg>
        <span className="sr-only">{isOpen ? "Close menu" : "Open menu"}</span>
      </button>
      <div id={panelId} hidden={!isOpen} className="col-span-2 min-w-0">
        <ul className="mt-2 border-t border-gray-200 py-2">
          {primaryNavigation.filter((item) => item.display !== false).map((item) => (
            <li key={item.href}>
              <Link href={item.href} className={controlClassName} onClick={closeNavigation}>
                {item.label}
              </Link>
            </li>
          ))}
          <li>
            <button type="button" aria-expanded={documentsOpen} aria-controls={documentsId}
              className={`${controlClassName} w-full justify-between`}
              onClick={() => setDocumentsOpen((open) => !open)}>
              Supporting Documents
              <span aria-hidden="true" className="shrink-0">{documentsOpen ? "−" : "+"}</span>
            </button>
            <ul id={documentsId} hidden={!documentsOpen} className="pl-4">
              {supportingDocumentsNavigation.filter((item) => item.display !== false).map((item) => (
                <li key={item.href}>
                  <Link href={item.href} className={controlClassName} onClick={closeNavigation}>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </li>
        </ul>
      </div>
    </nav>
  );
}
