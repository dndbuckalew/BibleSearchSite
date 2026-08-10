from pathlib import Path

print("===================================")
print("HCGO Initialization")
print("===================================")

# Root orchestration folder
root = Path(__file__).resolve().parent.parent

# Directories to create
directories = [
    root / "knowledge_asset_profiles",
    root / "knowledge_asset_profiles" / "bible_ta",
    root / "sass" / "persistence",
    root / "sass" / "publication",
]

# Placeholder files
files = [
    root / "knowledge_asset_profiles" / "bible_ta" / "kjv_profile.yaml",
    root / "README.md",
]

print("\nCreating Directories")

for directory in directories:
    if directory.exists():
        print(f"  ✓ Exists   : {directory}")
    else:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created : {directory}")

print("\nCreating Files")

for file in files:
    if file.exists():
        print(f"  ✓ Exists   : {file}")
    else:
        file.touch()
        print(f"  ✓ Created : {file}")

print("\nInitialization Complete")
