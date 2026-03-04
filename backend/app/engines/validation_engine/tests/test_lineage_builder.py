"""
Test Lineage Builder
"""
import pytest
from validation_engine.loaders.cim_loader import CIMLoader
from validation_engine.loaders.target_loader import Targets, SACModel
from validation_engine.lineage.lineage_builder import LineageBuilder


def test_lineage_builder_basic():
    """Test basic lineage graph construction"""
    mock_cim_data = {
        "metadata": {
            "universe_id": "test",
            "universe_name": "Test",
            "version": "1.0",
            "extracted_at": "2024-01-01T00:00:00"
        },
        "tables": [
            {"id": "ORDERS", "name": "ORDERS", "schema": "SALES", "columns": []}
        ],
        "dimensions": [
            {"id": "ORDER_ID", "name": "Order ID", "table": "ORDERS", "column": "ORDER_ID", "type": "dimension"}
        ],
        "measures": [
            {"id": "REVENUE", "name": "Revenue", "expression": "SUM(ORDERS.AMOUNT)", "aggregation": "SUM", "type": "measure"}
        ],
        "joins": []
    }

    loader = CIMLoader()
    cim = loader.load_from_dict(mock_cim_data)

    builder = LineageBuilder()
    graph = builder.build(cim, None)

    assert len(graph.nodes) > 0
    assert len(graph.edges) > 0

    # Check that table, dimension, and measure nodes exist
    node_types = {node["type"] for node in graph.nodes}
    assert "table" in node_types
    assert "dimension" in node_types
    assert "measure" in node_types


def test_lineage_builder_with_targets():
    """Test lineage graph with targets"""
    mock_cim_data = {
        "metadata": {
            "universe_id": "test",
            "universe_name": "Test",
            "version": "1.0",
            "extracted_at": "2024-01-01T00:00:00"
        },
        "tables": [],
        "dimensions": [
            {"id": "DIM1", "name": "Dimension 1", "table": "T1", "column": "C1", "type": "dimension"}
        ],
        "measures": [],
        "joins": []
    }

    loader = CIMLoader()
    cim = loader.load_from_dict(mock_cim_data)

    targets = Targets()
    targets.sac_model = SACModel(
        modelId="test_model",
        dimensions=[{"id": "DIM1", "name": "Dimension 1"}],
        measures=[]
    )

    builder = LineageBuilder()
    graph = builder.build(cim, targets)

    node_types = {node["type"] for node in graph.nodes}
    assert "sac_model" in node_types
    assert "sac_dimension" in node_types

    # Check that there's a transform edge
    edge_types = {edge["type"] for edge in graph.edges}
    assert "transforms_to" in edge_types
