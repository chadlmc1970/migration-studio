# BOBJ Binary Universe Parser - Java Bridge

## Problem

Real SAP BusinessObjects universes (like eFashion) use binary `.blx` and `.dfx` formats that require the SAP BusinessObjects Semantic Layer SDK to parse. The current Python parser only works with XML-based universes.

## Solution Overview

This directory contains a Java wrapper (`BLXParser.java`) that uses the SAP BusinessObjects SDK to extract metadata from binary `.blx` files.

## Requirements

The SAP BusinessObjects Semantic Layer SDK **authoring** components are required:
- `com.sap.sl.sdk.authoring.jar` - Authoring API
- `com.sap.sl.sdk.framework.jar` - SDK framework
- `com.sap.sl.sdk.jar` - Core SDK
- `com.businessobjects.semanticlayer.qt.jar` - Semantic layer
- `org.json` JAR for JSON output

## Current Status

**NOT WORKING** - The SDK JARs in `../sdk/BOBJ_SDK/` are from the **Information Design Tool** which only includes runtime/query APIs, NOT the authoring APIs needed to parse `.blx` files.

### What's Missing

The `com.sap.sl.sdk.authoring.*` packages are NOT included in the Information Design Tool distribution. They are only available in the full SDK with authoring components.

## Alternatives

### Option 1: Get Full SDK with Authoring Components

Download the full SAP BusinessObjects SDK that includes:
- SL SDK eclipse plugins with `com.sap.sl.sdk.authoring.jar`
- All authoring API dependencies

Place JARs in this directory's `lib/` folder and run `./build.sh`.

### Option 2: Export to XML (RECOMMENDED)

Use SAP Information Design Tool to export universes as XML:

1. Open universe in Information Design Tool
2. Right-click → Export → Universe Definition
3. Choose XML format
4. Use the exported XML with the Python parser

### Option 3: Use BOBJ REST API

If you have access to a BusinessObjects server:

```python
# Use RESTful Web Service SDK
# GET /universe/{id}/metadata
# Returns JSON with dimensions, measures, tables
```

### Option 4: Reverse Engineer Binary Format

The `.blx` and `.dfx` files are:
- ZIP archives containing binary data
- Inner files use proprietary serialization
- Would require significant reverse engineering

## File Structure

```
eFashion.unx (ZIP archive)
├── Properties (binary metadata)
├── eFashion.blx (ZIP archive → binary business layer)
│   └── eFashion.blx (binary - encrypted/proprietary)
├── eFashion.dfx (ZIP archive → binary data foundation)
│   └── eFashion.dfx (binary - encrypted/proprietary)
└── efashion_Unsecured.cnx (ZIP archive → connection info)
```

## Testing

If you have the authoring SDK:

```bash
./build.sh
./run_parser.sh /path/to/universe.blx /output/metadata.json
```

## Integration with Python Parser

Once working, integrate via:

```python
# In unx.py
import subprocess
import json

def parse_blx(blx_path):
    result = subprocess.run([
        './java_bridge/run_parser.sh',
        str(blx_path),
        '/tmp/metadata.json'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        with open('/tmp/metadata.json') as f:
            return json.load(f)
    else:
        raise Exception(f"BLX parsing failed: {result.stderr}")
```

## References

- [SAP BusinessObjects SDK Documentation](https://help.sap.com/docs/SAP_BUSINESSOBJECTS_BUSINESS_INTELLIGENCE_PLATFORM)
- [Semantic Layer SDK Guide](https://help.sap.com/doc/sdk_guide/)
- Sample code extracted from `com.sap.sl.sdk.authoring.samples.jar`

## Current Workaround

The Python parser now detects binary files and logs a warning with instructions. Empty structure is returned so the pipeline can continue, but manual intervention is required to get actual universe metadata.
