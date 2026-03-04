"""Semantic Graph Builder"""
import networkx as nx
from ..loaders.cim_loader import CIMModel


class SemanticGraph:
    """Build a semantic graph from CIM model"""

    def __init__(self, cim: CIMModel):
        self.cim = cim
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        """Build graph from tables and joins"""
        for table in self.cim.tables:
            self.graph.add_node(table.name, type="table")

        for join in self.cim.joins:
            self.graph.add_edge(
                join.left_table,
                join.right_table,
                join_type=join.type,
                condition=join.condition
            )

    def get_join_path(self, table_a: str, table_b: str) -> list[str]:
        """Find join path between two tables"""
        try:
            return nx.shortest_path(self.graph, table_a, table_b)
        except nx.NetworkXNoPath:
            return []

    def get_all_tables(self) -> list[str]:
        """Get all table names"""
        return list(self.graph.nodes())

    def is_connected(self) -> bool:
        """Check if all tables are connected"""
        return nx.is_connected(self.graph) if len(self.graph.nodes()) > 0 else True
