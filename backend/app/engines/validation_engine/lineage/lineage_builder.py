"""
Lineage Builder - constructs lineage graphs from CIM and targets
"""
from typing import Dict, Any, List, Set
import networkx as nx
from loaders.cim_loader import CIM
from loaders.target_loader import Targets


class LineageGraph:
    """Represents a lineage graph"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = []
        self.edges = []

    def add_node(self, node_id: str, node_type: str, attributes: Dict[str, Any] = None):
        """Add a node to the graph"""
        attrs = attributes or {}
        attrs["type"] = node_type

        self.graph.add_node(node_id, **attrs)

        self.nodes.append({
            "id": node_id,
            "type": node_type,
            **attrs
        })

    def add_edge(self, source: str, target: str, edge_type: str = "default", attributes: Dict[str, Any] = None):
        """Add an edge to the graph"""
        attrs = attributes or {}
        attrs["type"] = edge_type

        self.graph.add_edge(source, target, **attrs)

        self.edges.append({
            "source": source,
            "target": target,
            "type": edge_type,
            **attrs
        })

    def to_dict(self) -> Dict[str, Any]:
        """Export graph as dictionary"""
        # Convert nodes and edges to simple dicts (remove non-serializable types)
        serializable_nodes = []
        for node in self.nodes:
            node_dict = {}
            for key, value in node.items():
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    node_dict[key] = value
                else:
                    node_dict[key] = str(value)
            serializable_nodes.append(node_dict)

        serializable_edges = []
        for edge in self.edges:
            edge_dict = {}
            for key, value in edge.items():
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    edge_dict[key] = value
                else:
                    edge_dict[key] = str(value)
            serializable_edges.append(edge_dict)

        return {
            "nodes": serializable_nodes,
            "edges": serializable_edges,
            "stats": {
                "node_count": len(serializable_nodes),
                "edge_count": len(serializable_edges)
            }
        }


class LineageBuilder:
    """Builds lineage graphs from CIM and targets"""

    def build(self, cim: CIM, targets: Targets = None) -> LineageGraph:
        """
        Build lineage graph showing relationships between:
        - Tables
        - Dimensions
        - Measures
        - Target views
        """
        graph = LineageGraph()

        # Add CIM elements
        self._add_cim_elements(graph, cim)

        # Add target elements
        if targets:
            self._add_target_elements(graph, cim, targets)

        return graph

    def _add_cim_elements(self, graph: LineageGraph, cim: CIM):
        """Add CIM tables, dimensions, measures to graph"""

        # Add tables
        for table in cim.tables:
            graph.add_node(
                node_id=f"table:{table.name}",
                node_type="table",
                attributes={
                    "name": table.name,
                    "schema": table.schema,
                    "source": "cim"
                }
            )

        # Add dimensions
        for dim in cim.dimensions:
            dim_id = f"dimension:{dim.id}"
            graph.add_node(
                node_id=dim_id,
                node_type="dimension",
                attributes={
                    "name": dim.name,
                    "source_table": dim.table,
                    "source_column": dim.column,
                    "source": "cim"
                }
            )

            # Link dimension to table
            table_id = f"table:{dim.table}"
            if table_id in [n["id"] for n in graph.nodes]:
                graph.add_edge(
                    source=table_id,
                    target=dim_id,
                    edge_type="defines"
                )

        # Add measures
        for measure in cim.measures:
            measure_id = f"measure:{measure.id}"
            graph.add_node(
                node_id=measure_id,
                node_type="measure",
                attributes={
                    "name": measure.name,
                    "expression": measure.expression,
                    "aggregation": measure.aggregation,
                    "source": "cim"
                }
            )

            # Try to link measure to tables (parse expression)
            tables = self._extract_tables_from_expression(measure.expression)
            for table_name in tables:
                table_id = f"table:{table_name}"
                if table_id in [n["id"] for n in graph.nodes]:
                    graph.add_edge(
                        source=table_id,
                        target=measure_id,
                        edge_type="defines"
                    )

        # Add joins
        for join in cim.joins:
            left_id = f"table:{join.left_table}"
            right_id = f"table:{join.right_table}"

            graph.add_edge(
                source=left_id,
                target=right_id,
                edge_type="join",
                attributes={
                    "join_type": join.join_type,
                    "cardinality": join.cardinality,
                    "left_column": join.left_column,
                    "right_column": join.right_column
                }
            )

    def _add_target_elements(self, graph: LineageGraph, cim: CIM, targets: Targets):
        """Add target views and their relationships"""

        # Add SAC model
        if targets.sac_model:
            model_id = f"sac_model:{targets.sac_model.modelId}"
            graph.add_node(
                node_id=model_id,
                node_type="sac_model",
                attributes={
                    "name": targets.sac_model.modelId,
                    "source": "target"
                }
            )

            # Link SAC dimensions to CIM dimensions
            for dim in targets.sac_model.dimensions:
                sac_dim_id = f"sac_dimension:{dim.get('id', '')}"
                graph.add_node(
                    node_id=sac_dim_id,
                    node_type="sac_dimension",
                    attributes={
                        "name": dim.get("name", ""),
                        "source": "target"
                    }
                )

                # Link to model
                graph.add_edge(source=model_id, target=sac_dim_id, edge_type="contains")

                # Try to link to CIM dimension
                cim_dim_id = f"dimension:{dim.get('id', '')}"
                if cim_dim_id in [n["id"] for n in graph.nodes]:
                    graph.add_edge(
                        source=cim_dim_id,
                        target=sac_dim_id,
                        edge_type="transforms_to"
                    )

            # Link SAC measures to CIM measures
            for measure in targets.sac_model.measures:
                sac_measure_id = f"sac_measure:{measure.get('id', '')}"
                graph.add_node(
                    node_id=sac_measure_id,
                    node_type="sac_measure",
                    attributes={
                        "name": measure.get("name", ""),
                        "aggregation": measure.get("aggregation", ""),
                        "source": "target"
                    }
                )

                # Link to model
                graph.add_edge(source=model_id, target=sac_measure_id, edge_type="contains")

                # Try to link to CIM measure
                cim_measure_id = f"measure:{measure.get('id', '')}"
                if cim_measure_id in [n["id"] for n in graph.nodes]:
                    graph.add_edge(
                        source=cim_measure_id,
                        target=sac_measure_id,
                        edge_type="transforms_to"
                    )

        # Add Datasphere views
        for view in targets.datasphere_views:
            view_id = f"datasphere_view:{view.name}"
            graph.add_node(
                node_id=view_id,
                node_type="datasphere_view",
                attributes={
                    "name": view.name,
                    "source": "target"
                }
            )

            # Link view to source tables
            for table_name in view.tables:
                table_id = f"table:{table_name.upper()}"
                if table_id in [n["id"] for n in graph.nodes]:
                    graph.add_edge(
                        source=table_id,
                        target=view_id,
                        edge_type="used_by"
                    )

    def _extract_tables_from_expression(self, expression: str) -> Set[str]:
        """Extract table names from measure expression"""
        tables = set()

        # Simple pattern: TABLE.COLUMN
        parts = expression.split()
        for part in parts:
            if "." in part:
                table_part = part.split(".")[0].strip("(),")
                # Remove aggregation functions
                for func in ["SUM", "COUNT", "AVG", "MIN", "MAX"]:
                    table_part = table_part.replace(func, "").strip("()")
                if table_part and table_part.isalpha():
                    tables.add(table_part.upper())

        return tables
