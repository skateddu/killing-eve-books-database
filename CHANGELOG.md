# Changelog

All notable changes to this dataset will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

- Relationships for books 4–5 (*Resurrection*, *Long Shot*)
- Data for *Medusa* (when published)

## [1.0.0] - 2026-02-19

### Added

- **9 CSV tables**: books, chapters, characters, locations, organizations, glossary, characters_appearances, locations_appearances, relationships
- **170 characters** with roles, nationalities, aliases, and first appearance tracking
- **370 locations** in a hierarchical structure (continent → country → city → building)
- **51 organizations** with type classification
- **303 knowledge-graph relationships** (books 1–3)
- **512 glossary terms** with categories
- **122 chapters** with number and title per book
- **883 character appearances** and **581 location appearances** at chapter level
- SQLite schema with full DDL, foreign keys, indexes, and constraints
- Mermaid ER diagram
- Python import script (`main.py`) — stdlib only, no external dependencies
- GitHub Actions workflow for automated database builds
- Export script for Gephi (GEXF format)
- Dual-licensing: MIT for code (`LICENSE-CODE`), CC BY 4.0 for data (`LICENSE-DATA`)
- Academic citation metadata (`CITATION.cff`)
