from pathlib import Path
from zipfile import ZipFile

print("===================================")
print("HCGO SASS Source Inspection")
print("===================================")

# ------------------------------------------------------------------
# HCGO Domain Workspace
# ------------------------------------------------------------------

TAD_CONCEPTS_ROOT = Path(__file__).resolve().parents[5]

BTA_DOMAIN = TAD_CONCEPTS_ROOT / "HCGO Domain" / "BTA"

SOURCE_FOLDER = BTA_DOMAIN / "02_approved"
PROCESSING_FOLDER = BTA_DOMAIN / "03_processing"

# ------------------------------------------------------------------
# Locate approved artifact
# ------------------------------------------------------------------

print(f"Source Folder : {SOURCE_FOLDER}")
print(f"Exists        : {SOURCE_FOLDER.exists()}")
print()

zip_files = list(SOURCE_FOLDER.glob("*.zip"))

print(f"Approved Artifacts Found : {len(zip_files)}")

for zip_file in zip_files:
    print(f"  - {zip_file.name}")

if len(zip_files) != 1:
    raise RuntimeError(
        f"Expected exactly one approved artifact, found {len(zip_files)}."
    )

source_file = zip_files[0]
target_translation_folder = PROCESSING_FOLDER / source_file.stem

print()
print(f"Processing Folder : {PROCESSING_FOLDER}")
print(f"Source Artifact   : {source_file.name}")

print()
print(
    "Processing Folder :",
    "Found" if PROCESSING_FOLDER.exists() else "NOT Found",
)
print(
    "Source Artifact   :",
    "Found" if source_file.exists() else "NOT Found",
)

print()

target_translation_folder.mkdir(parents=True, exist_ok=True)

print(f"Extraction Folder : {target_translation_folder}")
print("Status            : Ready for extraction")

with ZipFile(source_file, "r") as zip_file:
    zip_file.extractall(target_translation_folder)

print("Status            : Extraction completed")
