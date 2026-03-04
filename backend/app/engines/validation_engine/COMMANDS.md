# Validation Engine - Command Reference

## Quick Start

```bash
cd ~/validation_engine
source venv/bin/activate
```

---

## Commands

### 1. Run Validation

```bash
# Validate all universes (respects pipeline state)
python cli.py run

# Validate specific universe
python cli.py run --universe sales_universe

# Generate mock data for testing
python cli.py run --generate-mocks

# Specify custom pipeline root
python cli.py run --pipeline-root /custom/path
```

### 2. List Universes

```bash
python cli.py list-universes
```

### 3. Run Tests

```bash
pytest tests/ -v
```

### 4. Run Demo

```bash
python demo.py
```

---

## Pipeline State Integration

### How It Works

1. **Before validation**, the engine reads `/pipeline/state/pipeline_state.json`
2. **Identifies universes** where `transformed=true` AND `validated!=true`
3. **After validation**, sets `validated=true` and writes timestamp
4. **Logs event** to `/pipeline/events/events.log`

### State File Format

```json
{
  "universes": {
    "sales_universe": {
      "parsed": true,
      "transformed": true,
      "validated": true,
      "validated_at": "2026-03-04T06:27:06.118656"
    }
  }
}
```

### Events Log

```
2026-03-04 06:27:06 validation completed sales_universe
```

---

## Output Files

### Location
```
/pipeline/validation/<universe_id>/
├── semantic_diff.json       # Missing/mismatched elements
├── coverage_report.json     # Coverage metrics
├── lineage_graph.json       # Lineage data (JSON)
└── lineage_graph.dot        # Lineage data (GraphViz)

/pipeline/logs/validation/
└── <universe_id>_validation_report.json
```

---

## Integration with Other Engines

### Typical Workflow

```bash
# 1. Universe Parser Engine
#    Produces: /pipeline/cim/sales_universe.cim.json
#    Sets: parsed=true

# 2. Transformation Engine
#    Produces: /pipeline/targets/sales_universe/*
#    Sets: transformed=true

# 3. Validation Engine (THIS ONE)
python cli.py run
#    Reads: CIM + targets
#    Produces: validation reports
#    Sets: validated=true
```

---

## CLI Options

### `run` command

| Option | Description | Default |
|--------|-------------|---------|
| `--pipeline-root`, `-p` | Pipeline root directory | `~/pipeline` |
| `--universe`, `-u` | Specific universe to validate | All ready universes |
| `--generate-mocks`, `-m` | Generate mock data | False |

### `list-universes` command

| Option | Description | Default |
|--------|-------------|---------|
| `--pipeline-root`, `-p` | Pipeline root directory | `~/pipeline` |

---

## Examples

### Example 1: Validate after transformation

```bash
# After transformation engine completes
cd ~/validation_engine
source venv/bin/activate
python cli.py run
```

### Example 2: Validate specific universe

```bash
python cli.py run --universe sales_universe
```

### Example 3: Check what's ready for validation

```bash
# Check pipeline state
cat ~/pipeline/state/pipeline_state.json

# List available universes
python cli.py list-universes
```

### Example 4: Generate and validate mock data

```bash
python cli.py run --generate-mocks
```

---

## Interpreting Results

### Semantic Validation

✅ **PASS**: All dimensions and measures found
⚠️ **WARNING**: Some aggregations don't match
❌ **FAIL**: Missing dimensions or measures

### Coverage Metrics

- **100%**: EXCELLENT - All elements preserved
- **80-99%**: GOOD - Most elements preserved
- **60-79%**: FAIR - Some elements missing
- **<60%**: POOR - Many elements missing

### Example Output

```
Summary:
  Dimensions: 3 checked, 0 missing
  Measures: 3 checked, 0 missing
  Joins: 2 checked, 1 missing

Coverage:
  table_coverage: 100.0%
  dimension_coverage: 100.0%
  measure_coverage: 100.0%
  join_coverage: 100.0%
```

---

## Troubleshooting

### CIM file not found

```bash
# Check CIM directory
ls ~/pipeline/cim/

# Generate mock data
python cli.py run --generate-mocks
```

### Targets not found

```bash
# Check targets directory
ls ~/pipeline/targets/sales_universe/

# Validation will continue with CIM only (0% coverage)
```

### Pydantic warning about schema

This is a known deprecation warning and can be ignored:
```
PydanticDeprecatedSince20: Support for class-based `config` is deprecated
```

---

## Performance

| Universe Size | Typical Runtime |
|---------------|-----------------|
| Small (3 tables, 10 dims) | ~15ms |
| Medium (20 tables, 100 dims) | ~100ms |
| Large (100 tables, 500 dims) | ~500ms |

---

## Exit Codes

- `0`: Success
- `1`: Failure (validation errors, exceptions)

---

## Environment Variables

None required. All configuration via CLI arguments.

---

## Advanced Usage

### Python API

```python
from pathlib import Path
from rich.console import Console
from runner import ValidationRunner

# Initialize
console = Console()
runner = ValidationRunner(
    pipeline_root=Path("/pipeline"),
    console=console
)

# Run validation
runner.run(universe_id="sales_universe")
```

### Custom Pipeline State Check

```python
from pipeline_state import PipelineStateManager
from pathlib import Path

state_mgr = PipelineStateManager(Path("/pipeline"))

# Get universes ready for validation
universes = state_mgr.get_universes_to_validate()
print(f"Ready: {universes}")

# Get specific universe state
state = state_mgr.get_universe_state("sales_universe")
print(f"State: {state}")
```

---

## Log Files

### Validation Report
```
/pipeline/logs/validation/sales_universe_validation_report.json
```

Contains:
- Universe ID
- Timestamp
- Dimensions/measures/joins checked
- Missing counts
- Coverage metrics
- Status

### Events Log
```
/pipeline/events/events.log
```

Appended with:
```
2026-03-04 06:27:06 validation completed sales_universe
```

---

## Next Steps

After validation completes:
1. Review validation reports
2. Check lineage graphs
3. Address any missing elements
4. Proceed to next pipeline stage (if any)

---

