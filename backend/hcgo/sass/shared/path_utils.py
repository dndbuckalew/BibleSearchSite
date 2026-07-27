"""
HCGO SASS Shared Utilities

Path Utility Functions

Provides domain-neutral helpers for working with filesystem paths.
"""

from pathlib import Path


def as_path(value: str | Path) -> Path:
    """
    Convert a string or Path into a pathlib.Path object.

    Args:
        value: Filesystem path as a string or Path.

    Returns:
        pathlib.Path
    """
    return value if isinstance(value, Path) else Path(value)


def ensure_directory(path: str | Path) -> Path:
    """
    Ensure a directory exists.

    Creates the directory (including parents) if necessary.

    Args:
        path: Directory path.

    Returns:
        pathlib.Path
    """
    directory = as_path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def resolve_path(path: str | Path) -> Path:
    """
    Return the fully resolved filesystem path.

    Args:
        path: Filesystem path.

    Returns:
        pathlib.Path
    """
    return as_path(path).resolve()


def path_exists(path: str | Path) -> bool:
    """
    Determine whether a filesystem path exists.

    Args:
        path: Filesystem path.

    Returns:
        True if the path exists.
    """
    return as_path(path).exists()
    