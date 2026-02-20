-- ============================================================
-- Killing Eve Books Database — SQLite Schema
-- ============================================================
-- This schema defines the relational structure for the
-- Killing Eve literary universe dataset.
-- Compatible with SQLite 3.x.
-- ============================================================

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------
-- Books
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    id               INTEGER PRIMARY KEY,
    title            TEXT    NOT NULL,
    author           TEXT    NOT NULL,
    publisher        TEXT,
    publication_date TEXT,           -- ISO 8601 date (YYYY-MM-DD)
    language         TEXT    NOT NULL DEFAULT 'english',
    pages            INTEGER,
    chapters         INTEGER
);

-- -----------------------------------------------------------
-- Chapters
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS chapters (
    id      INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id),
    chapter INTEGER NOT NULL,        -- chapter number within the book
    name    TEXT
);

CREATE INDEX IF NOT EXISTS idx_chapters_book_id ON chapters(book_id);

-- -----------------------------------------------------------
-- Characters
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS characters (
    id                       INTEGER PRIMARY KEY,
    name                     TEXT    NOT NULL,
    full_name                TEXT,
    aliases                  TEXT,   -- JSON array
    description              TEXT,
    role                     TEXT    CHECK (role IN ('protagonist', 'supporting', 'antagonist', 'minor', 'mentioned')),
    nationality              TEXT,
    gender                   TEXT    CHECK (gender IN ('male', 'female', 'non_binary', 'unknown')),
    first_appearance_book_id INTEGER REFERENCES books(id)
);

CREATE INDEX IF NOT EXISTS idx_characters_role ON characters(role);

-- -----------------------------------------------------------
-- Characters Appearances  (many-to-many: characters <-> chapters)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS characters_appearances (
    book_id      INTEGER NOT NULL REFERENCES books(id),
    chapter_id   INTEGER NOT NULL REFERENCES chapters(id),
    character_id INTEGER NOT NULL REFERENCES characters(id),
    PRIMARY KEY (book_id, chapter_id, character_id)
);

CREATE INDEX IF NOT EXISTS idx_char_app_character ON characters_appearances(character_id);
CREATE INDEX IF NOT EXISTS idx_char_app_chapter   ON characters_appearances(chapter_id);

-- -----------------------------------------------------------
-- Locations
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS locations (
    id              INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    location_type   TEXT,
    parent_location TEXT,            -- name of the parent location (hierarchical)
    description     TEXT,
    real_place      BOOLEAN          -- 1 = real, 0 = fictional
);

CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(location_type);

-- -----------------------------------------------------------
-- Locations Appearances  (many-to-many: locations <-> chapters)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS locations_appearances (
    book_id     INTEGER NOT NULL REFERENCES books(id),
    chapter_id  INTEGER NOT NULL REFERENCES chapters(id),
    location_id INTEGER NOT NULL REFERENCES locations(id),
    PRIMARY KEY (book_id, chapter_id, location_id)
);

CREATE INDEX IF NOT EXISTS idx_loc_app_location ON locations_appearances(location_id);
CREATE INDEX IF NOT EXISTS idx_loc_app_chapter  ON locations_appearances(chapter_id);

-- -----------------------------------------------------------
-- Organizations
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS organizations (
    id                       INTEGER PRIMARY KEY,
    name                     TEXT    NOT NULL,
    aliases                  TEXT,   -- JSON array
    organization_type        TEXT,
    description              TEXT,
    first_appearance_book_id INTEGER REFERENCES books(id)
);

CREATE INDEX IF NOT EXISTS idx_organizations_type ON organizations(organization_type);

-- -----------------------------------------------------------
-- Relationships  (knowledge graph triples)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS relationships (
    id           INTEGER PRIMARY KEY,
    book_id      INTEGER NOT NULL REFERENCES books(id),
    chapter_id   INTEGER NOT NULL REFERENCES chapters(id),
    subject_type TEXT    NOT NULL,
    subject_id   INTEGER NOT NULL,
    subject_name TEXT,
    predicate    TEXT    NOT NULL,
    object_type  TEXT    NOT NULL,
    object_id    INTEGER NOT NULL,
    object_name  TEXT
);

CREATE INDEX IF NOT EXISTS idx_rel_subject   ON relationships(subject_type, subject_id);
CREATE INDEX IF NOT EXISTS idx_rel_object    ON relationships(object_type, object_id);
CREATE INDEX IF NOT EXISTS idx_rel_predicate ON relationships(predicate);

-- -----------------------------------------------------------
-- Glossary
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS glossary (
    id          INTEGER PRIMARY KEY,
    term        TEXT    NOT NULL,
    category    TEXT,
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_glossary_category ON glossary(category);
