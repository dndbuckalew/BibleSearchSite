"use client";

import { useId, useState } from "react";

type ExpandableSectionProps = {
  preview: React.ReactNode;
  expanded: React.ReactNode;
};

export default function ExpandableSection({
  preview,
  expanded,
}: ExpandableSectionProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const contentId = useId();

  return (
    <div className="space-y-3">
      {preview}

      {!isExpanded && (
        <button
          type="button"
          aria-expanded={isExpanded}
          aria-controls={contentId}
          onClick={() => setIsExpanded(true)}
          className="text-base font-semibold text-blue-700 underline hover:text-blue-900"
        >
          ...More
        </button>
      )}

      <div id={contentId} hidden={!isExpanded}>
        {isExpanded && expanded}
      </div>

      {isExpanded && (
        <>
          <button
            type="button"
            aria-expanded={isExpanded}
            aria-controls={contentId}
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
