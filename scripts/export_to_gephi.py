"""Export the relationships table from the SQLite database to GEXF format for Gephi."""

import argparse
import logging
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(name=__name__)

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DEFAULT_DB: Path = PROJECT_ROOT / "database" / "killing_eve.db"
DEFAULT_OUTPUT: Path = PROJECT_ROOT / "database" / "killing_eve_graph.gexf"

GEXF_NAMESPACE: str = "http://www.gexf.net/1.3"
GEXF_VIZ_NAMESPACE: str = "http://www.gexf.net/1.3/viz"

NODE_COLORS: dict[str, dict[str, str]] = {
    "character":    {"r": "231", "g": "76",  "b": "60"},
    "organization": {"r": "46",  "g": "134", "b": "193"},
    "location":     {"r": "39",  "g": "174", "b": "96"},
}
"""RGB color mapping by entity type for Gephi visualization."""

DEFAULT_NODE_COLOR: dict[str, str] = {"r": "149", "g": "165", "b": "166"}


def _fetch_relationships(db_path: Path) -> list[sqlite3.Row]:
    """Fetch all relationship rows from the database.

    Parameters
    ----------
    db_path : Path
        Path to the SQLite database.

    Returns
    -------
    list[sqlite3.Row]
        All rows from the relationships table.
    """
    connection = sqlite3.connect(database=str(db_path))
    connection.row_factory = sqlite3.Row
    sql = """SELECT
        subject_type, subject_id, subject_name,
        predicate,
        object_type, object_id, object_name,
        book_id
    FROM relationships
    """
    rows = connection.execute(sql).fetchall()
    connection.close()
    return rows


def _collect_nodes(rows: list[sqlite3.Row]) -> dict[str, dict[str, str]]:
    """Extract unique nodes from relationship rows.

    Parameters
    ----------
    rows : list[sqlite3.Row]
        Relationship rows from the database.

    Returns
    -------
    dict[str, dict[str, str]]
        Mapping of node key to label and entity type.
    """
    nodes: dict[str, dict[str, str]] = {}
    for r in rows:
        for prefix in ("subject", "object"):
            key = f"{r[f'{prefix}_type']}_{r[f'{prefix}_id']}"
            if key not in nodes:
                nodes[key] = {
                    "label": r[f"{prefix}_name"] or key,
                    "type": r[f"{prefix}_type"],
                }
    return nodes


def _build_gexf_tree(
    nodes: dict[str, dict[str, str]],
    rows: list[sqlite3.Row],
) -> ET.ElementTree:
    """Build a GEXF XML tree from nodes and relationship edges.

    Parameters
    ----------
    nodes : dict[str, dict[str, str]]
        Unique graph nodes with label and type.
    rows : list[sqlite3.Row]
        Relationship rows used as directed edges.

    Returns
    -------
    ET.ElementTree
        Complete GEXF document ready for serialization.
    """
    gexf = ET.Element("gexf", xmlns=GEXF_NAMESPACE, version="1.3")
    gexf.set("xmlns:viz", GEXF_VIZ_NAMESPACE)

    meta = ET.SubElement(gexf, "meta")
    ET.SubElement(meta, "creator").text = "killing-eve-books-database"
    ET.SubElement(meta, "description").text = "Killing Eve Knowledge Graph"

    graph = ET.SubElement(gexf, "graph", defaultedgetype="directed", mode="static")

    node_attrs = ET.SubElement(graph, "attributes", **{"class": "node"})
    ET.SubElement(node_attrs, "attribute", id="0", title="entity_type", type="string")

    edge_attrs = ET.SubElement(graph, "attributes", **{"class": "edge"})
    ET.SubElement(edge_attrs, "attribute", id="0", title="book_id", type="integer")

    _add_nodes(graph, nodes)
    _add_edges(graph, rows)

    tree = ET.ElementTree(gexf)
    ET.indent(tree, space="  ")
    return tree


def _add_nodes(
    graph: ET.Element,
    nodes: dict[str, dict[str, str]],
) -> None:
    """Append node elements to the GEXF graph.

    Parameters
    ----------
    graph : ET.Element
        The ``<graph>`` XML element.
    nodes : dict[str, dict[str, str]]
        Unique graph nodes with label and type.
    """
    nodes_el = ET.SubElement(graph, "nodes")
    for node_id, info in nodes.items():
        node_el = ET.SubElement(nodes_el, "node", id=node_id, label=info["label"])
        attvalues = ET.SubElement(node_el, "attvalues")
        ET.SubElement(attvalues, "attvalue", **{"for": "0", "value": info["type"]})

        color = NODE_COLORS.get(info["type"], DEFAULT_NODE_COLOR)
        ET.SubElement(node_el, f"{{{GEXF_VIZ_NAMESPACE}}}color", **color)


def _add_edges(graph: ET.Element, rows: list[sqlite3.Row]) -> None:
    """Append edge elements to the GEXF graph.

    Parameters
    ----------
    graph : ET.Element
        The ``<graph>`` XML element.
    rows : list[sqlite3.Row]
        Relationship rows used as directed edges.
    """
    edges_el = ET.SubElement(graph, "edges")
    for i, r in enumerate(rows):
        source = f"{r['subject_type']}_{r['subject_id']}"
        target = f"{r['object_type']}_{r['object_id']}"
        edge_el = ET.SubElement(
            edges_el, "edge",
            id=str(i), source=source, target=target, label=r["predicate"],
        )
        attvalues = ET.SubElement(edge_el, "attvalues")
        ET.SubElement(attvalues, "attvalue", **{"for": "0", "value": str(r["book_id"])})


def export_gexf(db_path: Path, output_path: Path) -> None:
    """Read relationships from SQLite and write a GEXF file.

    Parameters
    ----------
    db_path : Path
        Path to the SQLite database.
    output_path : Path
        Destination path for the GEXF file.
    """
    rows = _fetch_relationships(db_path)
    nodes = _collect_nodes(rows)
    tree = _build_gexf_tree(nodes, rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(file_or_filename=str(output_path), encoding="utf-8", xml_declaration=True)
    logger.info("Exported %d nodes and %d edges to %s", len(nodes), len(rows), output_path)


def main() -> None:
    """CLI entry point: parse arguments and export the GEXF graph."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Export Killing Eve relationships to GEXF for Gephi.",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="Path to SQLite database")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output GEXF file path")
    args = parser.parse_args()

    if not args.db.exists():
        logger.error("Database not found: %s", args.db)
        logger.error("Run 'python main.py' first to build the database.")
        return

    export_gexf(args.db, args.output)


if __name__ == "__main__":
    main()
