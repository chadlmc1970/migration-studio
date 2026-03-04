"""BOBJ file format detection."""

import zipfile
from pathlib import Path


def detect_format(input_path: Path) -> str:
    """
    Detect BOBJ file format from extension and content.

    Supported formats:
    - .unx: Universe (UNX - ZIP-based)
    - .unv: Universe (UNV - binary)
    - .wid: WebI Document
    - .rpt: Crystal Report
    - .rep: WebI Report (older format)
    - .car: BIAR Archive

    Returns:
        Format string ('unx', 'unv', 'wid', 'rpt', 'rep', 'car')

    Raises:
        ValueError: If format cannot be determined
    """
    suffix = input_path.suffix.lower()

    # Extension-based detection
    format_map = {
        ".unx": "unx",
        ".unv": "unv",
        ".wid": "wid",
        ".rpt": "rpt",
        ".rep": "rep",
        ".car": "car",
    }

    if suffix in format_map:
        # Verify format by content for ZIP-based files
        if suffix in [".unx", ".wid", ".car", ".rep"]:
            if _is_valid_zip(input_path):
                return format_map[suffix]
            else:
                raise ValueError(f"File {input_path.name} has {suffix} extension but is not a valid ZIP archive")

        return format_map[suffix]

    # Content-based detection for files without standard extensions
    if _is_valid_zip(input_path):
        # Try to identify ZIP-based format by contents
        detected = _detect_zip_format(input_path)
        if detected:
            return detected

    raise ValueError(f"Unknown BOBJ format: {suffix}")


def _is_valid_zip(file_path: Path) -> bool:
    """Check if file is a valid ZIP archive."""
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            # Try to read file list
            zf.namelist()
            return True
    except (zipfile.BadZipFile, FileNotFoundError, PermissionError):
        return False


def _detect_zip_format(file_path: Path) -> str:
    """
    Detect format of ZIP-based BOBJ file by examining contents.

    Returns:
        Format string or empty string if cannot determine
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            file_list = zf.namelist()

            # WebI documents contain document.xml
            if "document.xml" in file_list or any("document.xml" in f.lower() for f in file_list):
                return "wid"

            # UNX universes contain .dfx or .blx files
            if any(f.endswith(".dfx") or f.endswith(".blx") for f in file_list):
                return "unx"

            # BIAR archives often contain manifest.xml or multiple .unv/.unx files
            has_manifest = any("manifest" in f.lower() for f in file_list)
            has_multiple_objects = sum(1 for f in file_list if f.endswith(('.unv', '.unx', '.wid', '.rpt'))) > 1
            if has_manifest or has_multiple_objects:
                return "car"

            # WebI .rep files (older format) - similar structure to .wid but different schema
            if any("report.xml" in f.lower() for f in file_list):
                return "rep"

    except Exception:
        pass

    return ""
