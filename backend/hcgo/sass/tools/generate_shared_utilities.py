"""
HCGO Source Acquisition & Staging Service (SASS)

Shared Utilities Generator

Purpose
-------
Framework for generating approved Shared Utility modules.
"""

from __future__ import annotations

from pathlib import Path
import argparse

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

SHARED_DIR = Path(__file__).resolve().parent.parent / "shared"

# Module templates will be added in the next implementation step.
MODULES: dict[str, str] = {}


# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------

def write_module(filename: str, content: str, overwrite: bool = False) -> str:
    """
    Write a generated module to the shared package.

    Returns:
        "created"
        "updated"
        "skipped"
    """

    target = SHARED_DIR / filename

    if target.exists():
        existed = True

        if target.read_text(encoding="utf-8").strip() and not overwrite:
            return "skipped"
    else:
        existed = False

    target.write_text(content.rstrip() + "\n", encoding="utf-8")

    return "updated" if existed else "created"


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:

    parser = argparse.ArgumentParser(
        description="Generate HCGO SASS Shared Utility modules."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing non-empty files.",
    )

    args = parser.parse_args()

    created = 0
    updated = 0
    skipped = 0

    for filename, content in MODULES.items():

        result = write_module(
            filename=filename,
            content=content,
            overwrite=args.force,
        )

        if result == "created":
            created += 1
        elif result == "updated":
            updated += 1
        else:
            skipped += 1

        print(f"{filename:<25} {result}")

    print("\nGeneration Summary")
    print("------------------")
    print(f"Created : {created}")
    print(f"Updated : {updated}")
    print(f"Skipped : {skipped}")


if __name__ == "__main__":
    main()
    