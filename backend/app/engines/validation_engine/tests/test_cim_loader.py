"""
Test CIM Loader
"""
import json
import pytest
from pathlib import Path
from validation_engine.loaders.cim_loader import CIMLoader, CIM


def test_cim_loader_basic():
    """Test basic CIM loading"""
    mock_cim_data = {
        "metadata": {
            "universe_id": "test_universe",
            "universe_name": "Test Universe",
            "version": "1.0",
            "extracted_at": "2024-01-01T00:00:00"
        },
        "tables": [
            {
                "id": "TABLE1",
                "name": "TABLE1",
                "schema": "SCHEMA1",
                "columns": []
            }
        ],
        "dimensions": [
            {
                "id": "DIM1",
                "name": "Dimension 1",
                "table": "TABLE1",
                "column": "COL1",
                "type": "dimension"
            }
        ],
        "measures": [
            {
                "id": "MEASURE1",
                "name": "Measure 1",
                "expression": "SUM(TABLE1.COL2)",
                "aggregation": "SUM",
                "type": "measure"
            }
        ],
        "joins": []
    }

    loader = CIMLoader()
    cim = loader.load_from_dict(mock_cim_data)

    assert cim.metadata.universe_id == "test_universe"
    assert len(cim.tables) == 1
    assert len(cim.dimensions) == 1
    assert len(cim.measures) == 1


def test_cim_loader_with_joins():
    """Test CIM loading with joins"""
    mock_cim_data = {
        "metadata": {
            "universe_id": "test_universe",
            "universe_name": "Test Universe",
            "version": "1.0",
            "extracted_at": "2024-01-01T00:00:00"
        },
        "tables": [],
        "dimensions": [],
        "measures": [],
        "joins": [
            {
                "id": "JOIN1",
                "left_table": "TABLE1",
                "right_table": "TABLE2",
                "left_column": "ID",
                "right_column": "ID",
                "join_type": "INNER",
                "cardinality": "1:N"
            }
        ]
    }

    loader = CIMLoader()
    cim = loader.load_from_dict(mock_cim_data)

    assert len(cim.joins) == 1
    assert cim.joins[0].join_type == "INNER"
