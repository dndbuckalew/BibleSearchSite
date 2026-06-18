"use client";

import { useState } from "react";

type ExpandableSectionProps = {
  preview: React.ReactNode;
  expanded: React.ReactNode;
};

export default function ExpandableSection({
  preview,
  expanded,
}: ExpandableSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="space-y-3">
      {preview}

      {!isExpanded && (
        <button
          type="button"
          onClick={() => setIsExpanded(true)}
          className="text-base font-semibold text-blue-700 underline hover:text-blue-900"
        >
          ...More
        </button>
      )}

      {isExpanded && (
        <>
          {expanded}

          <button
            type="button"
            onClick={() => setIsExpanded(false)}
            className="text-base font-semibold text-blue-700 underline hover:text-blue-900"
          >
            Show Less
          </button>
        </>
      )}
    </div>
  );
}
