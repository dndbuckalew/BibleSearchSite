"""
HCGO Domain Inventory

Displays the current contents of the HCGO Domain workspace.

Version: 6.0
"""

from pathlib import Path

TAD_CONCEPTS_ROOT = Path(__file__).resolve().parents[3]
ROOT = TAD_CONCEPTS_ROOT / "HCGO Domain"


def show_tree(folder: Path, indent: str = "") -> None:
    """Recursively display the HCGO Domain folder structure."""

    items = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))

    for item in items:
        if item.is_dir():
            print(f"{indent}[{item.name}]")
            show_tree(item, indent + "    ")
        else:
            print(f"{indent}- {item.name}")


def main() -> None:
    print("=" * 50)
    print("HCGO Domain Inventory")
    print("=" * 50)
    print(f"Root : {ROOT}")
    print()

    if not ROOT.exists():
        print("ERROR: HCGO Domain folder not found.")
        return

    show_tree(ROOT)

    print()
    print("=" * 50)
    print("Inventory Complete")
    print("=" * 50)


if __name__ == "__main__":
    main()
    