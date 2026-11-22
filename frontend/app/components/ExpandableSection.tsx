"use client";

import { useId, useState } from "react";

type ExpandableSectionProps = {
  preview: React.ReactNode;
  expanded: React.ReactNode;
  open?: boolean;
  onToggle?: (open: boolean) => void;
};

export default function ExpandableSection({
  preview,
  expanded,
  open,
  onToggle,
}: ExpandableSectionProps) {
  const [localOpen, setLocalOpen] = useState(false);
  const isExpanded = open ?? localOpen;
  const contentId = useId();

  return (
    <div className="space-y-3">
      {preview}

      <div id={contentId} hidden={!isExpanded}>
        {isExpanded && expanded}
      </div>

      <button
        type="button"
        aria-expanded={isExpanded}
        aria-controls={contentId}
        onClick={() => (onToggle ?? setLocalOpen)(!isExpanded)}
        className="text-base font-semibold text-blue-700 underline hover:text-blue-900"
      >
        {isExpanded ? "Show Less" : "More"}
      </button>
    </div>
  );
}
