"use client";

import { useState } from "react";

type ExpandableSectionProps = {
  title: string;
  blurb: string;
  text: string;
};

export default function ExpandableSection({
  title,
  blurb,
  text,
}: ExpandableSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="space-y-2">
      <button
        type="button"
        onClick={() => setIsExpanded((v) => !v)}
        aria-expanded={isExpanded}
        className="-mx-2 flex w-full items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-left transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-900/60"
      >
        <h3 className="text-xl font-medium text-neutral-900 dark:text-neutral-50">{title}</h3>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`h-5 w-5 shrink-0 text-neutral-500 transition-transform duration-200 ${
            isExpanded ? "rotate-180" : ""
          }`}
        >
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      <div className="text-sm text-neutral-600 dark:text-neutral-400">{blurb}</div>

      {isExpanded && (
        <div className="whitespace-pre-line text-neutral-900 dark:text-neutral-100">{text}</div>
      )}
    </div>
  );
}
