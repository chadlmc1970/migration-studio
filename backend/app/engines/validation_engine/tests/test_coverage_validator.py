"""
Test Coverage Validator
"""
import pytest
from validation_engine.loaders.cim_loader import CIMLoader
from validation_engine.loaders.target_loader import Targets, SACModel
from validation_engine.validators.coverage_validator import CoverageValidator


def test_coverage_validator_no_targets():
    """Test coverage when no targets exist"""
    mock_cim_data = {
        "metadata": {
            "universe_id": "test",
            "universe_name": "Test",
            "version": "1.0",
            "extracted_at": "2024-01-01T00:00:00"
        },
        "tables": [{"id": "T1", "name": "T1", "schema": "S1", "columns": []}],
        "dimensions": [{"id": "D1", "name": "D1", "table": "T1", "column": "C1", "type": "dimension"}],
        "measures": [{"id": "M1", "name": "M1", "expression": "SUM(T1.C2)", "aggregation": "SUM", "type": "measure"}],
        "joins": []
    }

    loader = CIMLoader()
    cim = loader.load_from_dict(mock_cim_data)

    validator = CoverageValidator()
    results = validator.validate(cim, None)

    assert results["dimension_coverage"] == 0.0
    assert results["measure_coverage"] == 0.0


def test_coverage_validator_full_coverage():
    """Test full coverage scenario"""
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
        "measures": [
            {"id": "MEASURE1", "name": "Measure 1", "expression": "SUM(T1.C2)", "aggregation": "SUM", "type": "measure"}
        ],
        "joins": []
    }

    loader = CIMLoader()
    cim = loader.load_from_dict(mock_cim_data)

    # Create mock targets with matching dimensions and measures
    targets = Targets()
    targets.sac_model = SACModel(
        modelId="test",
        dimensions=[{"id": "DIM1", "name": "Dimension 1"}],
        measures=[{"id": "MEASURE1", "name": "Measure 1", "aggregation": "SUM"}]
    )

    validator = CoverageValidator()
    results = validator.validate(cim, targets)

    assert results["dimension_coverage"] == 1.0
    assert results["measure_coverage"] == 1.0
