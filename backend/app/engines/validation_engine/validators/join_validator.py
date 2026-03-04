"""
Join Validator - validates join graph preservation
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from validation_engine.loaders.cim_loader import CIM, CIMJoin
from validation_engine.loaders.target_loader import Targets


class JoinValidator:
    """Validates that join graphs are preserved from CIM to targets"""

    def validate(self, cim: CIM, targets: Optional[Targets]) -> Dict[str, Any]:
        """
        Validate join preservation.

        Returns:
            {
                "joins_checked": int,
                "joins_found": int,
                "missing_joins": [...],
                "changed_joins": [...],
                "join_type_mismatches": [...]
            }
        """
        if targets is None:
            return {
                "joins_checked": len(cim.joins),
                "joins_found": 0,
                "missing_joins": [j.id for j in cim.joins],
                "changed_joins": [],
                "join_type_mismatches": []
            }

        # Build CIM join graph
        cim_join_graph = self._build_cim_join_graph(cim)

        # Build target join graph
        target_join_graph = self._build_target_join_graph(targets)

        # Compare graphs
        missing_joins = []
        changed_joins = []
        join_type_mismatches = []

        for join_key, cim_join in cim_join_graph.items():
            if join_key not in target_join_graph:
                # Check reverse direction
                reverse_key = (join_key[1], join_key[0])
                if reverse_key not in target_join_graph:
                    missing_joins.append({
                        "join_id": cim_join["id"],
                        "left_table": cim_join["left_table"],
                        "right_table": cim_join["right_table"],
                        "join_type": cim_join["join_type"]
                    })
                else:
                    # Found in reverse direction
                    target_join = target_join_graph[reverse_key]
                    if cim_join["join_type"] != target_join.get("type", "").split()[0]:
                        join_type_mismatches.append({
                            "join_id": cim_join["id"],
                            "expected_type": cim_join["join_type"],
                            "actual_type": target_join.get("type", "UNKNOWN"),
                            "note": "Found in reverse direction"
                        })
            else:
                # Join exists, check if it changed
                target_join = target_join_graph[join_key]

                # Check join type
                cim_type = cim_join["join_type"].upper()
                target_type = target_join.get("type", "").upper()

                if cim_type not in target_type and not self._join_types_compatible(cim_type, target_type):
                    join_type_mismatches.append({
                        "join_id": cim_join["id"],
                        "left_table": cim_join["left_table"],
                        "right_table": cim_join["right_table"],
                        "expected_type": cim_type,
                        "actual_type": target_type
                    })

        joins_found = len(cim.joins) - len(missing_joins)

        return {
            "joins_checked": len(cim.joins),
            "joins_found": joins_found,
            "missing_joins": missing_joins,
            "changed_joins": changed_joins,
            "join_type_mismatches": join_type_mismatches
        }

    def _build_cim_join_graph(self, cim: CIM) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Build join graph from CIM"""
        graph = {}

        for join in cim.joins:
            key = (join.left_table.upper(), join.right_table.upper())
            graph[key] = {
                "id": join.id,
                "left_table": join.left_table.upper(),
                "right_table": join.right_table.upper(),
                "left_column": join.left_column.upper(),
                "right_column": join.right_column.upper(),
                "join_type": join.join_type.upper(),
                "cardinality": join.cardinality
            }

        return graph

    def _build_target_join_graph(self, targets: Targets) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """Build join graph from target SQL"""
        graph = {}

        for view in targets.datasphere_views:
            tables = [t.upper() for t in view.tables]

            for join in view.joins:
                right_table = join.get("right_table", "").upper()
                join_type = join.get("type", "").upper()

                # Try to infer left table (previous table in list)
                if right_table and right_table in tables:
                    idx = tables.index(right_table)
                    if idx > 0:
                        left_table = tables[idx - 1]
                        key = (left_table, right_table)

                        graph[key] = {
                            "left_table": left_table,
                            "right_table": right_table,
                            "type": join_type,
                            "condition": join.get("condition", "")
                        }

        return graph

    def _join_types_compatible(self, cim_type: str, target_type: str) -> bool:
        """Check if join types are compatible"""
        # Simple compatibility check
        cim_type = cim_type.upper()
        target_type = target_type.upper()

        if cim_type == target_type:
            return True

        # INNER and JOIN are compatible
        if cim_type == "INNER" and "INNER" in target_type:
            return True

        if cim_type == "LEFT" and "LEFT" in target_type:
            return True

        if cim_type == "RIGHT" and "RIGHT" in target_type:
            return True

        return False
