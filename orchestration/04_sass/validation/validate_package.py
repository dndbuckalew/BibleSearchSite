from pathlib import Path
import json

print("===================================")
print("HCGO SASS Package Validation")
print("===================================")

# ------------------------------------------------------------------
# HCGO Domain Workspace
# ------------------------------------------------------------------

TAD_CONCEPTS_ROOT = Path(__file__).resolve().parents[5]

BTA_DOMAIN = TAD_CONCEPTS_ROOT / "HCGO Domain" / "BTA"

PACKAGE = (
    BTA_DOMAIN
    / "03_processing"
    / "validation"
    / "VALIDATION_KJV"
)

print(f"Validation Package : {PACKAGE}")
print(f"Exists             : {PACKAGE.exists()}")
print()

if not PACKAGE.exists():
    print(f"ERROR: Package not found:\n{PACKAGE}")
    raise SystemExit(1)

required_files = [
    "manifest.json",
    "translation.json",
    "books.json",
    "chapters.json",
    "verses.json",
    "verse_text.json",
    "validation_metadata.json",
]

missing = []

for file_name in required_files:
    file_path = PACKAGE / file_name

    if file_path.exists():
        print(f"✓ {file_name}")
    else:
        print(f"✗ {file_name}")
        missing.append(file_name)

print()

if missing:
    print("VALIDATION FAILED")
    print("-----------------")
    print("Missing Files:")

    for file_name in missing:
        print(f"  - {file_name}")

    raise SystemExit(1)

print("VALIDATION PASSED")
