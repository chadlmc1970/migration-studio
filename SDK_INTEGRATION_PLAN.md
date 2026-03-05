# SAP BusinessObjects SDK - Wholistic Integration Plan

## Overview

Integrate SAP BOBJ SDK into the migration tool to parse binary UNV files with full metadata extraction (tables, joins, dimensions, measures, contexts, prompts, connection info).

## Current Status

### ✅ Completed
- SDK extraction architecture (sdk_bridge.py)
- JPype integration setup
- UNV extractor with SDK fallback (io/unv.py)
- Setup automation script (setup_sdk.sh)
- README documentation

### 🚧 Pending
- Complete `_open_universe()` implementation
- Discover actual SDK class names from JARs
- Test with real UNV files
- Integrate into full pipeline

## SDK Integration Steps

### Step 1: Extract & Setup SDK (In Progress)
```bash
# Extraction running now (3-5 min)
cd ~/Desktop && unzip BOBJ_SDK.zip

# Move to project
mv ~/Desktop/SAP\ BusinessObjects ~/migration_studio/backend/app/engines/bobj2sac/sdk/BOBJ_SDK

# Run setup
cd ~/migration_studio && ./setup_sdk.sh
```

**What setup_sdk.sh does:**
- ✅ Verifies 1,645 JAR files present
- ✅ Installs Java OpenJDK 11
- ✅ Installs JPype (Python-Java bridge)
- ✅ Tests JVM startup with SDK JARs
- ✅ Lists available SDK classes

### Step 2: Discover SDK Classes

Once JVM starts, we need to find the correct class names:

```bash
# List classes in universe JAR
jar tf backend/app/engines/bobj2sac/sdk/BOBJ_SDK/java/lib/*.jar | grep -i universe | grep "\.class$"
```

**Key classes we're looking for:**
- Universe opening/loading class
- Universe metadata API
- Table/Join/Dimension/Measure classes
- Context and Prompt classes
- Connection info class

### Step 3: Implement `_open_universe()`

Location: `backend/app/engines/bobj2sac/sdk_bridge.py:152`

**Current code:**
```python
def _open_universe(self, unv_path: Path):
    raise NotImplementedError("Implement once we verify SDK JAR contents")
```

**Expected implementation pattern:**
```python
def _open_universe(self, unv_path: Path):
    from com.businessobjects.rebean.wi import Universe
    # OR
    from com.crystaldecisions.sdk.occa.universe import IUniverse

    # Open the .unv file
    universe = Universe.load(str(unv_path))
    # OR
    universe = UniverseFactory.openUniverse(str(unv_path))

    return universe
```

### Step 4: Complete Extraction Methods

All extraction methods are **ready** but depend on correct SDK class structure:

**Already implemented:**
- ✅ `_extract_universe_metadata()` - name, id, description, version
- ✅ `_extract_tables()` - name, type, SQL, description
- ✅ `_extract_joins()` - left/right table, type, condition, cardinality
- ✅ `_extract_dimensions()` - name, table, column, type, qualification
- ✅ `_extract_measures()` - name, table, column, aggregation, formula
- ✅ `_extract_contexts()` - resolve ambiguous join paths
- ✅ `_extract_prompts()` - LOVs and user input filters
- ✅ `_extract_connection_info()` - database connection details

**What might need adjustment:**
- Method names (e.g., `getName()` vs `get_name()` vs `name()`)
- Attribute access (e.g., `universe.tables` vs `universe.getTables()`)
- Type conversions (Java types → Python types)

### Step 5: Test with Real UNV Files

**Test files available:**
```
/Users/I870089/pipeline/input/Version 2 - for SAP BI 4.x/
├── BOEXI40-Audit-DB2.unx (contains .unv inside)
├── BOEXI40-Audit-HANA.unx
├── BOEXI40-Audit-MSSQL.unx
├── BOEXI40-Audit-MySQL.unx
├── BOEXI40-Audit-Oracle.unx
├── BOEXI40-Audit-SQLAnywhere.unx
└── BOEXI40-Audit-Sybase.unx
```

**Note**: These are `.unx` files (ZIP format), not `.unv` (binary). We need to:
1. Extract .unx to find .unv inside
2. Test SDK with the binary .unv file

**Test command:**
```python
from pathlib import Path
from backend.app.engines.bobj2sac.sdk_bridge import BOBJSDKBridge, UNVParser
from backend.app.engines.bobj2sac.util.logging import ConversionLogger

# Start JVM
BOBJSDKBridge.start_jvm()

# Parse UNV
logger = ConversionLogger()
parser = UNVParser()
unv_path = Path("/path/to/extracted/universe.unv")
cim_data = parser.parse_universe(unv_path)

print(f"✓ Tables: {len(cim_data['tables'])}")
print(f"✓ Joins: {len(cim_data['joins'])}")
print(f"✓ Dimensions: {len(cim_data['dimensions'])}")
print(f"✓ Measures: {len(cim_data['measures'])}")
print(f"✓ Contexts: {len(cim_data['contexts'])}")
```

### Step 6: Pipeline Integration

The integration is **already done** in `io/unv.py`:

```python
if SDK_AVAILABLE:
    try:
        logger.log("Using SAP BusinessObjects SDK for UNV parsing")
        parser = UNVParser()
        cim_data = parser.parse_universe(input_path)
        _populate_cim_from_sdk(cim, cim_data, logger)

        # Advanced features
        if cim_data.get('contexts'):
            logger.log(f"  - {len(cim_data['contexts'])} contexts extracted")

        if cim_data.get('prompts'):
            logger.log(f"  - {len(cim_data['prompts'])} prompts/LOVs extracted")
    except NotImplementedError:
        logger.warn("SDK parser not fully implemented - using placeholder")
        _create_placeholder_cim(cim, logger)
```

**When SDK is ready:**
1. Upload .unx file → Unzips to .unv
2. Parser calls `extract_unv()`
3. SDK opens .unv and extracts full metadata
4. CIM populated with tables, joins, dims, measures, contexts, prompts
5. Transform stage creates SAC models with richer metadata
6. Validation stage has more data to validate

### Step 7: Verify End-to-End

**Upload → Parse → Transform → Validate:**

1. Upload a BOEXI40 universe through frontend
2. Check logs for "Using SAP BusinessObjects SDK for UNV parsing"
3. Verify CIM has:
   - Real table names (not placeholders)
   - Actual joins with conditions
   - Dimensions with qualifications
   - Measures with aggregations
   - **NEW**: Contexts extracted
   - **NEW**: Prompts/LOVs extracted
   - **NEW**: Connection info extracted
4. Verify SAC model includes:
   - Proper dimension hierarchies
   - Correct measure formulas
   - Context-aware relationships
5. Verify validation report shows:
   - 100% coverage (not 0% placeholder)
   - Semantic diff with actual comparisons
   - Lineage graph with real relationships

## Expected Outcomes

### Before SDK (Current)
```json
{
  "tables": [],
  "joins": [],
  "dimensions": [],
  "measures": [],
  "metadata": {
    "note": "UNV binary format requires SAP SDK. Placeholder created."
  }
}
```

### After SDK (Target)
```json
{
  "tables": [
    {"name": "SALES_FACT", "type": "table", "sql": "SELECT * FROM SALES"},
    {"name": "CUSTOMER_DIM", "type": "table", "sql": "SELECT * FROM CUSTOMER"}
  ],
  "joins": [
    {
      "left_table": "SALES_FACT",
      "right_table": "CUSTOMER_DIM",
      "type": "inner",
      "condition": "SALES_FACT.CUSTOMER_ID = CUSTOMER_DIM.ID",
      "cardinality": "N:1"
    }
  ],
  "dimensions": [
    {
      "name": "Customer Name",
      "table": "CUSTOMER_DIM",
      "column": "NAME",
      "type": "string",
      "qualification": "dimension"
    }
  ],
  "measures": [
    {
      "name": "Revenue",
      "table": "SALES_FACT",
      "column": "AMOUNT",
      "aggregation": "SUM",
      "formula": "SUM(SALES_FACT.AMOUNT)"
    }
  ],
  "contexts": [
    {
      "name": "Sales Context",
      "joins": ["SALES_FACT.CUSTOMER_ID = CUSTOMER_DIM.ID"],
      "description": "Resolve customer dimension via sales fact"
    }
  ],
  "prompts": [
    {
      "name": "Year Prompt",
      "type": "single",
      "query": "SELECT DISTINCT YEAR FROM SALES_FACT",
      "default_value": "2024"
    }
  ],
  "connection": {
    "type": "HANA",
    "database": "SALES_DB",
    "server": "hana.example.com:30015"
  }
}
```

## Timeline

1. **Now - 5 min**: SDK extraction completes
2. **5-10 min**: Run setup_sdk.sh (install Java, JPype, test JVM)
3. **10-20 min**: Discover SDK classes, implement `_open_universe()`
4. **20-30 min**: Test with real UNV file, verify extraction
5. **30-40 min**: End-to-end pipeline test
6. **40-50 min**: Deploy to production (optional)

## Troubleshooting

### "SDK classes not found"
```bash
# List all classes in JARs
for jar in backend/app/engines/bobj2sac/sdk/BOBJ_SDK/**/*.jar; do
    echo "=== $jar ==="
    jar tf "$jar" | grep -i universe | head -5
done
```

### "JVM failed to start"
```bash
# Check Java version
java -version  # Should be 11.x.x

# Test JPype
python3 -c "import jpype; print(jpype.__version__)"
```

### "Method not found on universe object"
```python
# Introspect universe object
universe = parser._open_universe(unv_path)
print(dir(universe))  # List all methods
print(type(universe))  # Show class type
```

## Success Criteria

✅ JVM starts with all 1,645 SDK JARs loaded
✅ `_open_universe()` successfully opens .unv file
✅ All extraction methods return real data (not empty lists)
✅ CIM populated with tables, joins, dimensions, measures
✅ **Advanced features extracted**: contexts, prompts, connection info
✅ Pipeline processes UNV files without placeholder warnings
✅ SAC models contain rich metadata from SDK extraction
✅ Validation reports show 100% coverage

## Next Actions (Once Extraction Completes)

1. Move SDK to project: `mv ~/Desktop/"SAP BusinessObjects" ~/migration_studio/backend/app/engines/bobj2sac/sdk/BOBJ_SDK`
2. Run setup: `cd ~/migration_studio && ./setup_sdk.sh`
3. Discover classes: Inspect JAR contents
4. Complete implementation: Fill in `_open_universe()`
5. Test: Process a real UNV file
6. Deploy: Push to production (already has SDK code, just needs JARs)
