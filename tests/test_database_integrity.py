"""Database integrity tests."""

import json
import logging
import sqlite3
import sys
from pathlib import Path

logger = logging.getLogger(name=__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "killing_eve.db"

# Expected minimum row counts per table (should only grow over time).
EXPECTED_MIN_COUNTS = {
    "books": 6,
    "chapters": 122,
    "characters": 170,
    "locations": 370,
    "organizations": 51,
    "glossary": 512,
    "characters_appearances": 883,
    "locations_appearances": 581,
    "relationships": 303,
}


def get_connection() -> sqlite3.Connection:
    """Return a connection to the database with foreign keys enabled.

    Returns
    -------
    sqlite3.Connection
        Open connection to the test database.

    Raises
    ------
    FileNotFoundError
        If the database file does not exist.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run 'python main.py' first."
        )
    connection = sqlite3.connect(database=str(DB_PATH))
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# ── Row count checks ──────────────────────────────────────────────


def test_table_row_counts():
    """Each table should have at least the expected number of rows."""
    connection = get_connection()
    for table, expected_min in EXPECTED_MIN_COUNTS.items():
        (actual,) = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        assert actual >= expected_min, (
            f"{table}: expected >= {expected_min} rows, got {actual}"
        )
    connection.close()


# ── Foreign key integrity ─────────────────────────────────────────


def test_foreign_key_integrity():
    """No foreign key violations should exist in the database."""
    connection = get_connection()
    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    connection.close()
    assert violations == [], f"Foreign key violations found: {violations}"


# ── Referential checks ────────────────────────────────────────────


def test_chapters_reference_valid_books():
    """Every chapter should reference an existing book."""
    connection = get_connection()
    sql = """SELECT c.id, c.book_id FROM chapters c
    LEFT JOIN books b ON b.id = c.book_id
    WHERE b.id IS NULL
    """
    orphans = connection.execute(sql).fetchall()
    connection.close()
    assert orphans == [], f"Chapters with invalid book_id: {orphans}"


def test_characters_appearances_references():
    """Every character appearance should reference valid book, chapter, and character."""
    connection = get_connection()
    sql = """SELECT ca.book_id, ca.chapter_id, ca.character_id
    FROM characters_appearances ca
    LEFT JOIN books b ON b.id = ca.book_id
    LEFT JOIN chapters ch ON ch.id = ca.chapter_id
    LEFT JOIN characters c ON c.id = ca.character_id
    WHERE b.id IS NULL OR ch.id IS NULL OR c.id IS NULL
    """
    orphans = connection.execute(sql).fetchall()
    connection.close()
    assert orphans == [], f"Character appearances with broken references: {orphans}"


def test_locations_appearances_references():
    """Every location appearance should reference valid book, chapter, and location."""
    connection = get_connection()
    sql = """SELECT la.book_id, la.chapter_id, la.location_id
    FROM locations_appearances la
    LEFT JOIN books b ON b.id = la.book_id
    LEFT JOIN chapters ch ON ch.id = la.chapter_id
    LEFT JOIN locations l ON l.id = la.location_id
    WHERE b.id IS NULL OR ch.id IS NULL OR l.id IS NULL
    """
    orphans = connection.execute(sql).fetchall()
    connection.close()
    assert orphans == [], f"Location appearances with broken references: {orphans}"


def test_relationships_reference_valid_chapters():
    """Every relationship should reference a valid book and chapter."""
    connection = get_connection()
    sql = """SELECT r.id, r.book_id, r.chapter_id
    FROM relationships r
    LEFT JOIN books b ON b.id = r.book_id
    LEFT JOIN chapters ch ON ch.id = r.chapter_id
    WHERE b.id IS NULL OR ch.id IS NULL
    """
    orphans = connection.execute(sql).fetchall()
    connection.close()
    assert orphans == [], f"Relationships with broken references: {orphans}"


def test_relationships_polymorphic_fk():
    """Every subject/object in relationships should reference an existing entity."""
    type_table_map = {
        "character": "characters",
        "organization": "organizations",
        "location": "locations",
    }
    connection = get_connection()
    rows = connection.execute(
        "SELECT id, subject_type, subject_id, object_type, object_id FROM relationships"
    ).fetchall()

    broken = []
    for rel_id, s_type, s_id, o_type, o_id in rows:
        for label, etype, eid in [("subject", s_type, s_id), ("object", o_type, o_id)]:
            table = type_table_map.get(etype)
            if table is None:
                broken.append(
                    f"rel {rel_id}: unknown {label}_type '{etype}'"
                )
                continue
            (exists,) = connection.execute(
                f"SELECT COUNT(*) FROM {table} WHERE id = ?", (eid,)
            ).fetchone()
            if exists == 0:
                broken.append(
                    f"rel {rel_id}: {label} {etype}:{eid} not found in {table}"
                )

    connection.close()
    assert broken == [], (
        "Polymorphic FK violations in relationships:\n" + "\n".join(broken)
    )


# ── Data quality checks ───────────────────────────────────────────


def test_no_empty_names():
    """Key name columns should never be NULL or empty."""
    connection = get_connection()
    checks = [
        ("books", "title"),
        ("characters", "name"),
        ("locations", "name"),
        ("organizations", "name"),
        ("glossary", "term"),
    ]
    for table, col in checks:
        (count,) = connection.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL OR TRIM({col}) = ''"
        ).fetchone()
        assert count == 0, f"{table}.{col} has {count} NULL/empty values"
    connection.close()


def test_aliases_are_valid_json():
    """Aliases columns should contain valid JSON arrays."""
    connection = get_connection()
    for table in ("characters", "organizations"):
        rows = connection.execute(f"SELECT id, name, aliases FROM {table}").fetchall()
        for row_id, name, aliases in rows:
            if aliases is not None:
                try:
                    parsed = json.loads(s=aliases)
                    assert isinstance(parsed, list), (
                        f"{table} id={row_id} ({name}): aliases is not a JSON array"
                    )
                except json.JSONDecodeError:
                    raise AssertionError(
                        f"{table} id={row_id} ({name}): invalid JSON in aliases: {aliases!r}"
                    )
    connection.close()


# ── Run without pytest ────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            logger.info("  PASS  %s", test_fn.__name__)
            passed += 1
        except (AssertionError, FileNotFoundError) as exc:
            logger.error("  FAIL  %s: %s", test_fn.__name__, exc)
            failed += 1

    logger.info("\n%d passed, %d failed", passed, failed)
    sys.exit(1 if failed else 0)
