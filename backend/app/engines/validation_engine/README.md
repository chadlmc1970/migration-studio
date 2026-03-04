# Validation and Lineage Engine

Validation and Lineage Engine for SAP Migration System - validates semantic preservation and generates lineage graphs.

## Features

- **Semantic Validation**: Validates dimensions, measures, and aggregations
- **Coverage Analysis**: Computes coverage metrics for tables, dimensions, measures, and joins
- **Join Validation**: Verifies join graph preservation
- **Lineage Graphs**: Generates NetworkX graphs showing data flow
- **Multiple Export Formats**: JSON, DOT (GraphViz)

## Installation

```bash
cd validation_engine
pip install -e .
```

## Usage

### Run Validation

```bash
# Validate all universes
python cli.py run

# Validate specific universe
python cli.py run --universe sales_universe

# Generate mock data for testing
python cli.py run --generate-mocks
```

### List Universes

```bash
python cli.py list-universes
```

## Pipeline Structure

```
pipeline/
├── cim/                    # CIM files from Universe Parser
│   └── sales_universe.cim.json
├── targets/                # Generated artifacts from Transformation Engine
│   └── sales_universe/
│       ├── sac/model.json
│       ├── datasphere/views.sql
│       └── hana/schema.sql
├── validation/             # Validation outputs (this engine)
│   └── sales_universe/
│       ├── semantic_diff.json
│       ├── coverage_report.json
│       └── lineage_graph.json
└── logs/
    └── validation/
        └── sales_universe_validation_report.json
```

## Output Files

### semantic_diff.json
Shows differences between CIM and generated models:
- Missing dimensions
- Missing measures
- Aggregation mismatches

### coverage_report.json
Coverage metrics:
- Table coverage
- Dimension coverage
- Measure coverage
- Join coverage

### lineage_graph.json
Lineage graph with nodes and edges showing relationships between:
- Tables
- Dimensions
- Measures
- Target views

## Testing

```bash
pytest tests/
```

## Architecture

```
validation_engine/
├── cli.py                  # CLI entry point
├── runner.py               # Orchestration
├── loaders/
│   ├── cim_loader.py      # Load CIM files
│   └── target_loader.py   # Load target artifacts
├── validators/
│   ├── coverage_validator.py
│   ├── join_validator.py
│   └── semantic_validator.py
├── lineage/
│   ├── lineage_builder.py
│   └── graph_export.py
└── reports/
    ├── diff_report.py
    └── coverage_report.py
```
