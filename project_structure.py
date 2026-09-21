"""
Scaffolds the geo-intelligence-platform project directory structure.

Usage:
    python create_project_structure.py
"""

from pathlib import Path

# Creates the structure in the current directory (no new root folder)
ROOT = Path(".")

# Folders to create
FOLDERS = [
    "data/raw",
    "data/processed",
    "data/curated",
    "src/ingestion",
    "src/processing",
    "src/analytics",
    "tests",
    "notebooks",
]

# Empty files to create at the root
FILES = [
    "requirements.txt",
    ".gitignore",
    "README.md",
]


def create_structure():
    for folder in FOLDERS:
        path = ROOT / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created: {path}")

    for file in FILES:
        path = ROOT / file
        path.touch(exist_ok=True)
        print(f"Created: {path}")

    print(f"\nProject structure created under: {ROOT.resolve()}")


if __name__ == "__main__":
    create_structure()