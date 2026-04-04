# Killing Eve Books Database

[![Build SQLite Database](https://github.com/skateddu/killing-eve-books-database/actions/workflows/build-database.yml/badge.svg)](https://github.com/skateddu/killing-eve-books-database/actions/workflows/build-database.yml)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE-CODE)
[![License: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Kaggle Dataset](https://img.shields.io/badge/Kaggle-dataset-20BEFF.svg?logo=kaggle&logoColor=white)](https://www.kaggle.com/datasets/skateddu/killing-eve-books-database)
[![GitHub last commit](https://img.shields.io/github/last-commit/skateddu/claude-code-python-setup)](https://github.com/skateddu/claude-code-python-setup/commits/main)

> **[Unofficial]** A comprehensive structured database & Knowledge Graph of the complete Killing Eve literary universe by Luke Jennings.

Covers all published novels plus the upcoming *Medusa* and *Blueblood*, with **characters**, **locations**, **organizations**, **relationships**, **glossary terms**, and chapter-level appearance tracking — all manually curated for accuracy.

---

> **⚠️ Spoiler Alert:** This dataset contains detailed information about characters, relationships, and plot events from all published Killing Eve books. If you haven't read the series yet, be aware that browsing the data **will reveal major spoilers**.

## Overview

This dataset captures the narrative universe of the *Killing Eve* book series in a fully relational format. Here are some directions it enables:

- **Network & graph analysis**: Import the `relationships` table into a graph tool (Gephi, NetworkX, Neo4j) to study character centrality, community detection, and how the network evolves across books
- **Narrative structure**: Analyze chapter-level character and location appearances to map pacing, POV shifts, and parallel storylines
- **Geographic analysis**: Plot locations on a map to visualize the geographic scope of each book, track character movements, and compare real vs. fictional places
- **Character evolution**: Track how character roles and relationships change across the series (e.g. allies becoming enemies)
- **NLP & information extraction**: Use the structured data as ground truth to benchmark entity extraction, relation extraction, or summarization models against the original texts
- **Fan reference**: A searchable encyclopedia of the entire book series

## Books Covered

| # | Title | Publisher | Date | Pages | Chapters |
| --- | --- | --- | --- | ---: | :---: |
| 1 | Codename Villanelle | Hodder & Stoughton | 2017-06-29 | 224 | 4 |
| 2 | No Tomorrow | Hodder & Stoughton | 2018-10-25 | 256 | 8 |
| 3 | Die For Me | Hodder & Stoughton | 2020-04-09 | 240 | 14 |
| 4 | Resurrection | Boldwood Books | 2025-06-02 | 256 | 46 |
| 5 | Long Shot | Boldwood Books | 2025-11-01 | 264 | 50 |
| 6 | Medusa | Boldwood Books | 2026-05-11 | 264 | 49 |
| 7 | Blueblood | Boldwood Books | 2026-11-01 | — | — |

## Project Structure

```text
killing-eve-books-database/
├── .github/
│   ├── workflows/
│   │   └── build-database.yml      # CI: auto-build SQLite on data changes
│   └── ISSUE_TEMPLATE/             # Templates for bug reports & proposals
├── data/                           # CSV dataset files
├── schema/
│   ├── datasette-metadata.json     # Datasette metadata for web browsing
│   ├── er_diagram.mmd              # Mermaid ER diagram
│   └── schema.sql                  # SQLite DDL (CREATE TABLE statements)          
├── scripts/
│   ├── export_to_gephi.py          # Export relationships to GEXF for Gephi
│   └── export_to_jsonld.py         # Export CSV data to JSON-LD
├── tests/
│   └── test_database_integrity.py  # DB integrity & data quality checks
├── database/                       # Generated SQLite database (gitignored)
├── main.py                         # CSV → SQLite import script
├── pyproject.toml                  # Python project metadata
├── CHANGELOG.md                    # Version history
├── CITATION.cff                    # Citation metadata for academics
├── LICENSE-CODE                    # MIT (code)
├── LICENSE-DATA                    # CC BY 4.0 (dataset)
└── README.md
```

## Quick Start

### Use the CSV files directly

The `data/` folder contains all tables as CSV files. Load them with any tool: Python, R, Excel, etc.

```python
import csv

with open(file="data/characters.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["role"])
```

### Download the pre-built database

A ready-to-use `killing_eve.db` file is available for download from the [**Releases**](../../releases/latest) page — no Python required.

### Build from source

Requires **Python 3.10+** (no external dependencies — uses only the standard library).

```bash
python main.py
```

This creates `database/killing_eve.db`. You can then query it:

```bash
sqlite3 database/killing_eve.db "SELECT name, role FROM characters WHERE role = 'protagonist';"
```

To specify a custom output path:

```bash
python main.py --db path/to/my_database.db
```

### Explore on Kaggle

The full dataset is available on Kaggle with an interactive Quickstart notebook:

📊 [**Dataset**](https://www.kaggle.com/datasets/skateddu/killing-eve-books-database)
📓 [**Quickstart Notebook**](https://www.kaggle.com/code/skateddu/quickstart-exploring-the-killing-eve-universe)

## Dataset Structure

```text
data/
├── books.csv                   # title, author, publisher, dates
├── chapters.csv                # chapter number and title per book
├── characters.csv              # name, aliases, role, nationality, gender
├── characters_appearances.csv  # which character appears in which chapter
├── locations.csv               # hierarchical (continent → country → city → building)
├── locations_appearances.csv   # which location appears in which chapter
├── organizations.csv           # criminal, intelligence, commercial
├── relationships.csv           # knowledge-graph triples (subject → predicate → object)
└── glossary.csv                # cultural references, slang, technical terms
```

### Entity-Relationship Diagram

The full ER diagram is available in Mermaid format at [`schema/er_diagram.mmd`](schema/er_diagram.mmd).

```mermaid
erDiagram
    books ||--o{ chapters : "has"
    books ||--o{ organizations : "first_appearance"
    chapters ||--o{ characters_appearances : "appears_in"
    chapters ||--o{ locations_appearances : "appears_in"
    chapters ||--o{ relationships : "established_in"
    characters ||--o{ characters_appearances : "appears"
    locations ||--o{ locations_appearances : "appears"
```

### Table Reference

<details>
<summary>Click to expand full column details for all tables</summary>

#### `books`

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `title` | TEXT | Book title |
| `author` | TEXT | Author name |
| `publisher` | TEXT | Publisher |
| `publication_date` | TEXT | ISO 8601 date |
| `language` | TEXT | Language |
| `pages` | INTEGER | Page count |
| `chapters` | INTEGER | Chapter count |

#### `chapters`

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `book_id` | INTEGER | FK → books |
| `chapter` | INTEGER | Chapter number within book |
| `name` | TEXT | Chapter title |

#### `characters`

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `name` | TEXT | Common name |
| `full_name` | TEXT | Full name (if known) |
| `aliases` | TEXT | Known aliases |
| `description` | TEXT | Character description |
| `role` | TEXT | `protagonist` / `supporting` / `antagonist` / `minor` / `mentioned` |
| `nationality` | TEXT | Nationality |
| `gender` | TEXT | Gender |

#### `locations`

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `name` | TEXT | Location name |
| `location_type` | TEXT | `continent` / `country` / `region` / `city` / `building` / ... |
| `parent_location` | TEXT | Parent in the location hierarchy |
| `description` | TEXT | Description |
| `real_place` | BOOLEAN | `TRUE` = real, `FALSE` = fictional |

#### `organizations`

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `name` | TEXT | Organization name |
| `aliases` | TEXT | Known aliases |
| `organization_type` | TEXT | `criminal` / `intelligence_agency` / `commercial` / ... |
| `description` | TEXT | Description |
| `first_appearance_book_id` | INTEGER | FK → books |

#### `relationships` (Knowledge Graph)

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `book_id` | INTEGER | FK → books |
| `chapter_id` | INTEGER | FK → chapters |
| `subject_type` | TEXT | `character` / `organization` / `location` |
| `subject_id` | INTEGER | Subject entity ID |
| `subject_name` | TEXT | Subject name |
| `predicate` | TEXT | Relationship type (e.g. `works_for`, `child_of`) |
| `object_type` | TEXT | `character` / `organization` / `location` |
| `object_id` | INTEGER | Object entity ID |
| `object_name` | TEXT | Object name |

#### `glossary`

| Column | Type | Description |
| --- | --- | --- |
| `id` | INTEGER | Primary key |
| `term` | TEXT | Term |
| `category` | TEXT | Category (e.g. `cultural_reference`, `slang`, `technical_term`) |
| `description` | TEXT | Definition / explanation |

#### Junction Tables

- **`characters_appearances`** — (`book_id`, `chapter_id`, `character_id`)
- **`locations_appearances`** — (`book_id`, `chapter_id`, `location_id`)

</details>

## Scripts & Tools

### Export to GEXF (Gephi)

```bash
python scripts/export_to_gephi.py
```

Generates `database/killing_eve_graph.gexf`, ready to open in [Gephi](https://gephi.org/).

### Export to JSON-LD

```bash
python scripts/export_to_jsonld.py
```

Reads the CSV files directly and generates `database/killing_eve_ld.json` — a single [JSON-LD](https://json-ld.org/) document with [Schema.org](https://schema.org/) vocabulary, ready for linked data and semantic web applications.

### Browse with Datasette

```bash
pip install datasette
datasette database/killing_eve.db --metadata schema/datasette-metadata.json
```

Launches a web interface at `http://localhost:8001` to explore the database interactively.

### Verify database integrity

```bash
python tests/test_database_integrity.py
```

### Recommended tools

| Tool | Use case | Link |
| --- | --- | --- |
| **Datasette** | Publish the SQLite database as an explorable web interface | [datasette.io](https://datasette.io/) |
| **DB Browser for SQLite** | Browse tables, run queries, inspect the full database visually | [sqlitebrowser.org](https://sqlitebrowser.org/) |
| **DuckDB** | Query CSV files directly with SQL, no database build needed | [duckdb.org](https://duckdb.org/) |
| **Gephi** | Visualize and analyze the knowledge graph as a network | [gephi.org](https://gephi.org/) |
| **Kepler.gl** | Map-based visualization of locations data | [kepler.gl](https://kepler.gl/) |

## Data Criteria

How each table is populated:

- **`characters`**, **`locations`**, **`organizations`** — All entities identified in the text are recorded, regardless of narrative relevance (protagonists, minor mentions, background details).
- **`characters_appearances`** — A character is listed in a chapter only if **physically present** in the scene (including remote participation, e.g. phone calls), not merely mentioned by other characters.
- **`locations_appearances`** — A location is listed only if it is an **active setting** where events take place, not merely referenced in dialogue or narration.
- **`relationships`** — Knowledge-graph triples extracted per chapter. Entity order follows the **global order of first appearance** across the book.
- **`glossary`** — Curated selection of noteworthy terms: foreign words, cultural and historical references, slang, technical terms, weapons, food & drink, titles and ranks, and proper names.

## Data Generation

This dataset was built through a multi-stage pipeline combining text processing, semantic chunking, agentic AI extraction, and manual curation.

### Pipeline overview

```text
Books (raw text)
  │
  ├─ 1. Chapter splitting (regex-based, per-book separator analysis)
  │
  ├─ 2. Semantic chunking (Chonkie — SemanticChunker)
  │     └─ Long chapters split into narratively coherent segments
  │
  ├─ 3. Agentic entity & relationship extraction (Agno + SQL tool)
  │     ├─ Agent reads each chunk with full schema awareness
  │     ├─ Identifies entities (characters, locations, organizations)
  │     ├─ Extracts relationships as knowledge-graph triples
  │     └─ Populates a PostgreSQL database (Docker + volume)
  │
  ├─ 4. Manual curation & semantic cleanup (Claude Code)
  │     └─ Reviewed and refined for consistency, deduplication, and accuracy
  │
  └─ 5. Export to CSV → SQLite
```

### Tools & models used

| Stage | Tool | Role |
| --- | --- | --- |
| Chapter splitting | Python `re` | Regex-based splitting after analyzing per-book chapter separators |
| Semantic chunking | [**Chonkie**](https://github.com/chonkie-inc/chonkie) | `SemanticChunker` to segment long chapters into narratively coherent pieces |
| AI agent framework | [**Agno**](https://github.com/agno-agi/agno) | Orchestrates the extraction agent with a SQL tool and schema context |
| Extraction model | [**Gemini 3 Flash Preview**](https://openrouter.ai/google/gemini-3-flash-preview) via [OpenRouter](https://openrouter.ai/) | Entity recognition and relationship extraction |
| Staging database | [**PostgreSQL**](https://www.postgresql.org/) (Docker) | Intermediate structured storage during extraction |
| Manual curation | [**Claude Code**](https://docs.anthropic.com/en/docs/claude-code) | Semantic cleanup, deduplication, consistency checks, and refinement |

### Why this approach?

- **Semantic chunking** ensures the AI agent processes narratively meaningful segments rather than arbitrary fixed-size windows, improving extraction quality
- **Agentic SQL extraction** allows the model to directly populate a relational schema, enforcing structural consistency from the start
- **Human-in-the-loop curation** catches hallucinations, resolves ambiguities, and ensures the final dataset faithfully represents the source material

## Contributing

Contributions are welcome! If you find inaccuracies or want to add data (e.g. for *Medusa* when released), please open an issue or submit a pull request.

I'm also happy to hear **proposals and ideas** — whether it's corrections to the data, suggestions for new tables or fields, or entirely new directions for the project (analysis scripts, visualizations, integrations, etc.). Feel free to open an issue to start a discussion.

### For non-technical contributors

The full dataset is available as a **read-only Google Drive folder** where you can view the tables data and suggest corrections or additions via comments:

📂 [**Open Google Drive folder**](https://drive.google.com/drive/folders/1J9EwqRHUvA4vYyKWvkzntSij1pa0PQ4o?usp=sharing)

## License

This project uses a **dual-license** model:

| Component | License | File |
| --- | --- | --- |
| **Dataset** (CSV files, schema, ER diagram) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | [LICENSE-DATA](LICENSE-DATA) |
| **Code** (Python scripts, tests, CI workflow) | [MIT](https://opensource.org/licenses/MIT) | [LICENSE-CODE](LICENSE-CODE) |

The CC BY 4.0 license applies to the **structure, compilation, and organization** of the database — not to the underlying narrative content of the *Killing Eve* novels, which remains the intellectual property of Luke Jennings and his publishers.

> **Disclaimer:** This is an unofficial fan-made dataset. *Killing Eve* and all related characters, names, and storylines are the intellectual property of Luke Jennings and their respective publishers ([Hodder & Stoughton](https://www.hodder.co.uk/), [Boldwood Books](https://www.boldwoodbooks.com/)). The character descriptions and relationship data included in this dataset are provided under the principles of fair use / fair dealing, strictly for research, analysis, and educational purposes. If you are a rights holder and have concerns, please [open an issue](../../issues).

## Acknowledgments

This project exists thanks to the brilliant work of **Luke Jennings**, whose *Killing Eve* novels created a rich and compelling universe that made this dataset possible. All original characters, storylines, and narrative elements are his creation. Copyright for the original books belongs to Luke Jennings and his publishers ([Hodder & Stoughton](https://www.hodder.co.uk/), [Boldwood Books](https://www.boldwoodbooks.com/)).
