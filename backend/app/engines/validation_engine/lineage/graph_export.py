"""
Graph Exporter - exports lineage graphs to various formats
"""
import json
from pathlib import Path
from typing import Dict, Any
from lineage.lineage_builder import LineageGraph


class GraphExporter:
    """Exports lineage graphs to JSON, NetworkX, and DOT formats"""

    def export_json(self, graph: LineageGraph, output_path: Path):
        """Export graph as JSON"""
        with open(output_path, "w") as f:
            json.dump(graph.to_dict(), f, indent=2)

    def export_dot(self, graph: LineageGraph, output_path: Path):
        """Export graph as GraphViz DOT file"""
        lines = ["digraph lineage {"]
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=box, style=rounded];")
        lines.append("")

        # Define node styles by type
        node_styles = {
            "table": 'shape=cylinder, style=filled, fillcolor=lightblue',
            "dimension": 'shape=ellipse, style=filled, fillcolor=lightgreen',
            "measure": 'shape=diamond, style=filled, fillcolor=lightyellow',
            "sac_model": 'shape=box, style=filled, fillcolor=orange',
            "sac_dimension": 'shape=ellipse, style=filled, fillcolor=lightcoral',
            "sac_measure": 'shape=diamond, style=filled, fillcolor=lightcoral',
            "datasphere_view": 'shape=box, style=filled, fillcolor=lightgray'
        }

        # Add nodes
        for node in graph.nodes:
            node_id = self._escape_dot_id(node["id"])
            node_type = node["type"]
            node_label = node.get("name", node["id"])

            style = node_styles.get(node_type, 'shape=box')

            lines.append(f'  "{node_id}" [label="{node_label}", {style}];')

        lines.append("")

        # Define edge styles by type
        edge_styles = {
            "defines": 'color=blue',
            "join": 'color=red, style=dashed',
            "contains": 'color=green',
            "transforms_to": 'color=purple, style=bold',
            "used_by": 'color=gray'
        }

        # Add edges
        for edge in graph.edges:
            source = self._escape_dot_id(edge["source"])
            target = self._escape_dot_id(edge["target"])
            edge_type = edge.get("type", "default")

            style = edge_styles.get(edge_type, 'color=black')

            lines.append(f'  "{source}" -> "{target}" [{style}];')

        lines.append("}")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

    def export_networkx(self, graph: LineageGraph):
        """Return NetworkX graph object"""
        return graph.graph

    def _escape_dot_id(self, node_id: str) -> str:
        """Escape special characters for DOT format"""
        return node_id.replace(":", "_").replace(" ", "_")
