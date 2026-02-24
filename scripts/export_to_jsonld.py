"""Export CSV data files to a single JSON-LD document."""

import argparse
import csv
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(name=__name__)

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"
DATABASE_DIR: Path = PROJECT_ROOT / "database"
DEFAULT_OUTPUT: Path = DATABASE_DIR / "killing_eve_ld.json"

TABLES: list[str] = [
    "books",
    "chapters",
    "characters",
    "characters_appearances",
    "locations",
    "locations_appearances",
    "organizations",
    "relationships",
    "glossary",
]
"""CSV basenames (without extension), in logical order."""

JSONLD_CONTEXT: dict = {
    "@vocab": "https://schema.org/",
    "ke": "https://github.com/skateddu/killing-eve-books-database/schema#",
    "books": {"@id": "ke:books", "@type": "Book"},
    "chapters": {"@id": "ke:chapters", "@type": "ke:Chapter"},
    "characters": {"@id": "ke:characters", "@type": "Person"},
    "locations": {"@id": "ke:locations", "@type": "Place"},
    "organizations": {"@id": "ke:organizations", "@type": "Organization"},
    "relationships": {"@id": "ke:relationships", "@type": "ke:Relationship"},
    "glossary": {"@id": "ke:glossary", "@type": "DefinedTerm"},
    "characters_appearances": {"@id": "ke:characters_appearances", "@type": "ke:Appearance"},
    "locations_appearances": {"@id": "ke:locations_appearances", "@type": "ke:Appearance"},
}
"""JSON-LD context mapping tables to Schema.org and custom vocabulary."""

ALIAS_TABLES: set[str] = {"characters", "organizations"}
"""Tables whose ``aliases`` column contains a Python-like list that needs JSON parsing."""


def _parse_aliases(raw: str) -> list[str]:
    """Convert a Python-like alias string to a native list.

    Parameters
    ----------
    raw : str
        Raw alias value from CSV, e.g. ``"['Oxana' 'Maria']"``.

    Returns
    -------
    list[str]
        Parsed aliases, or an empty list when input is blank.
    """
    if not raw or not raw.strip():
        return []
    return re.findall(pattern=r"'([^']+)'", string=raw)


def _coerce_value(value: str) -> str | int | bool | None:
    """Coerce a raw CSV cell to the most appropriate JSON type.

    Parameters
    ----------
    value : str
        Raw cell value from the CSV reader.

    Returns
    -------
    str | int | bool | None
        Coerced value.
    """
    if value == "":
        return None
    if value.upper() == "TRUE":
        return True
    if value.upper() == "FALSE":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def _read_csv(table: str) -> list[dict]:
    """Read a single CSV file and return coerced rows.

    Parameters
    ----------
    table : str
        Table name (matches the CSV filename without extension).

    Returns
    -------
    list[dict]
        Rows as dictionaries with coerced values.
    """
    csv_path = DATA_DIR / f"{table}.csv"
    parse_aliases = table in ALIAS_TABLES

    with open(file=csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: list[dict] = []
        for raw_row in reader:
            row = {col: _coerce_value(val) for col, val in raw_row.items()}
            if parse_aliases:
                row["aliases"] = _parse_aliases(raw_row.get("aliases", ""))
            rows.append(row)

    return rows


def export_jsonld(output_path: Path) -> None:
    """Read all CSV files and write a single JSON-LD document.

    Parameters
    ----------
    output_path : Path
        Destination path for the JSON-LD file.
    """
    document: dict = {
        "@context": JSONLD_CONTEXT,
        "@id": "https://github.com/skateddu/killing-eve-books-database",
        "name": "Killing Eve Books Database",
        "description": (
            "A comprehensive structured database and knowledge graph "
            "of the complete Killing Eve literary universe by Luke Jennings."
        ),
    }

    total = 0
    for table in TABLES:
        rows = _read_csv(table)
        document[table] = rows
        total += len(rows)
        logger.info("  %-28s ← %s.csv (%s rows)", table, table, f"{len(rows):,}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Done. %s total rows exported to %s", f"{total:,}", output_path.name)


def main() -> None:
    """CLI entry point: parse arguments and export JSON-LD."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Export Killing Eve CSV data to JSON-LD.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output JSON-LD file path (default: {DEFAULT_OUTPUT.name})",
    )
    args = parser.parse_args()

    export_jsonld(args.output)


if __name__ == "__main__":
    main()
