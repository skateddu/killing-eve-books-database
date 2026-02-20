"""Import all CSV files from data/ into a SQLite database."""

import argparse
import csv
import json
import logging
import re
import sqlite3
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(name=__name__)

PROJECT_ROOT: Path = Path(__file__).resolve().parent
SCHEMA_PATH: Path = PROJECT_ROOT / "schema" / "schema.sql"
DATA_DIR: Path = PROJECT_ROOT / "data"
DATABASE_DIR: Path = PROJECT_ROOT / "database"
DEFAULT_DB: Path = DATABASE_DIR / "killing_eve.db"

TABLE_CSV_MAP: list[tuple[str, str]] = [
    ("books", "books.csv"),
    ("chapters", "chapters.csv"),
    ("characters", "characters.csv"),
    ("locations", "locations.csv"),
    ("organizations", "organizations.csv"),
    ("glossary", "glossary.csv"),
    ("characters_appearances", "characters_appearances.csv"),
    ("locations_appearances", "locations_appearances.csv"),
    ("relationships", "relationships.csv"),
]
"""Ordered so that parent tables are populated before children (FK safety)."""

COLUMN_RENAMES: dict[str, dict[str, str]] = {
    "organizations": {
        "fist_appearance_book_id": "first_appearance_book_id",
    },
}
"""Map CSV column names to DB column names when they differ (e.g. typos in source)."""


def _aliases_to_json(raw: str) -> str:
    """Convert a Python-like alias list to a JSON array.

    Parameters
    ----------
    raw : str
        Raw alias string from CSV, e.g. ``"['Oxana' 'Maria']"``.

    Returns
    -------
    str
        JSON array string, e.g. ``'["Oxana", "Maria"]'``. Returns ``"[]"``
        when input is empty or contains no quoted values.
    """
    if not raw or not raw.strip():
        return "[]"
    matches = re.findall(pattern=r"'([^']+)'", string=raw)
    return json.dumps(obj=matches, ensure_ascii=False) if matches else "[]"


COLUMN_TRANSFORMS: dict[str, dict[str, Callable[[str], str]]] = {
    "characters":    {"aliases": _aliases_to_json},
    "organizations": {"aliases": _aliases_to_json},
}
"""Per-table, per-column value transforms applied during import."""


def create_schema(connection: sqlite3.Connection) -> None:
    """Execute the DDL script to create all tables.

    Parameters
    ----------
    connection : sqlite3.Connection
        Open database connection.
    """
    ddl = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(ddl)


def _coerce_value(value: str, transform: Callable[[str], str] | None) -> str | int | None:
    """Coerce a single CSV cell value for SQLite insertion.

    Parameters
    ----------
    value : str
        Raw cell value from the CSV reader.
    transform : Callable[[str], str] | None
        Optional column-specific transform function.

    Returns
    -------
    str | int | None
        Transformed value ready for SQLite insertion.
    """
    if transform is not None:
        return transform(value)
    if value == "":
        return None
    if value.upper() == "TRUE":
        return 1
    if value.upper() == "FALSE":
        return 0
    return value


def import_csv(connection: sqlite3.Connection, table: str, csv_path: Path) -> int:
    """Import a single CSV file into the given table.

    Parameters
    ----------
    connection : sqlite3.Connection
        Open database connection.
    table : str
        Target table name.
    csv_path : Path
        Path to the source CSV file.

    Returns
    -------
    int
        Number of rows imported.

    Raises
    ------
    ValueError
        If the CSV file has no header row.
    """
    renames = COLUMN_RENAMES.get(table, {})
    transforms = COLUMN_TRANSFORMS.get(table, {})

    with open(file=csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_columns = reader.fieldnames
        if csv_columns is None:
            raise ValueError(f"No header found in {csv_path}")

        db_columns = [renames.get(c, c) for c in csv_columns]
        placeholders = ", ".join(["?"] * len(db_columns))
        col_names = ", ".join(db_columns)
        sql = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"

        rows: list[list[str | int | None]] = [
            [_coerce_value(row[col], transforms.get(col)) for col in csv_columns]
            for row in reader
        ]

        connection.executemany(sql, rows)
    return len(rows)


def _build_database(db_path: Path) -> None:
    """Build the SQLite database from schema and CSV files.

    Parameters
    ----------
    db_path : Path
        Output path for the SQLite database file.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        db_path.unlink()
        logger.info("Removed existing database: %s", db_path)

    connection = sqlite3.connect(database=str(db_path))
    try:
        create_schema(connection)
        logger.info("Schema created successfully.")

        total = 0
        for table, csv_file in TABLE_CSV_MAP:
            csv_path = DATA_DIR / csv_file
            if not csv_path.exists():
                logger.warning("SKIP  %s (file not found)", csv_file)
                continue
            count = import_csv(connection, table, csv_path)
            total += count
            logger.info("  %-28s ← %-35s (%s rows)", table, csv_file, f"{count:,}")

        connection.commit()
        logger.info("Done. %s total rows imported into %s", f"{total:,}", db_path.name)
    finally:
        connection.close()


def main() -> None:
    """CLI entry point: parse arguments and build the database."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Import Killing Eve CSV data into SQLite.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"Path to the output SQLite database (default: {DEFAULT_DB.name})",
    )
    args = parser.parse_args()

    _build_database(args.db)


if __name__ == "__main__":
    main()
