# SAP BusinessObjects SDK Integration

## Overview

This directory contains the SAP BusinessObjects SDK integration layer for parsing binary UNV universe files.

## Setup Instructions

### 1. Extract SDK from Windows Installer

**On Windows (Parallels):**
1. Run the SAP installer: `BIPLATCLNT4400_0-80008792.EXE`
2. Complete installation wizard
3. SDK JARs will be extracted to: `Desktop\BOBJ_SDK`

### 2. Copy JARs to Mac

**Transfer from Windows to Mac:**
1. Drag `BOBJ_SDK` folder from Windows Desktop to Mac Desktop
2. Move to project:
   ```bash
   cd ~/migration_studio
   mkdir -p backend/app/engines/bobj2sac/sdk
   mv ~/Desktop/BOBJ_SDK backend/app/engines/bobj2sac/sdk/
   ```

### 3. Run Setup Script

```bash
cd ~/migration_studio
./setup_sdk.sh
```

This will:
- ✅ Install Java OpenJDK 11
- ✅ Install JPype (Python-Java bridge)
- ✅ Test SDK integration
- ✅ Verify JVM startup with SDK JARs

## Architecture

```
sdk_bridge.py          # Python-Java bridge using JPype
├── BOBJSDKBridge      # JVM lifecycle management
├── UNVParser          # Parse .unv binary files
└── SDKInfo            # SDK introspection utilities

io/unv.py              # Enhanced UNV extractor
├── extract_unv()      # Main extraction function
├── Uses SDK if available
└── Falls back to placeholder if SDK missing
```

## Usage

### Test SDK Connection

```python
from backend.app.engines.bobj2sac.sdk_bridge import BOBJSDKBridge, SDKInfo

# Start JVM
BOBJSDKBridge.start_jvm()

# Get SDK version
version = SDKInfo.get_sdk_version()
print(f"SDK Version: {version}")

# Shutdown when done
BOBJSDKBridge.shutdown_jvm()
```

### Parse UNV File

```python
from pathlib import Path
from backend.app.engines.bobj2sac.io.unv import extract_unv
from backend.app.engines.bobj2sac.util.logging import ConversionLogger

logger = ConversionLogger()
input_path = Path("universes/Sales.unv")
output_dir = Path("output/sales")

# Extract with SDK
cim = extract_unv(input_path, output_dir, logger)

print(f"Extracted {len(cim.dimensions)} dimensions")
print(f"Extracted {len(cim.measures)} measures")
```

## What Gets Extracted

### Basic Metadata (Available Now)
- ✅ Universe name, ID, description
- ✅ Tables (name, type, SQL)
- ✅ Joins (left/right table, type, condition)
- ✅ Dimensions (name, table, column, description)
- ✅ Measures (name, table, column, aggregation, formula)

### Advanced Metadata (With SDK)
- 🎯 **Contexts** - Resolve ambiguous join paths
- 🎯 **Prompts/LOVs** - User input filters with cascading
- 🎯 **Connection Info** - Database connection details
- 🎯 **Complex Formulas** - Business logic calculations
- 🎯 **Aggregate Awareness** - Performance optimization hints
- 🎯 **Security/Rights** - Access control metadata

## SDK Implementation Status

### ✅ Completed
- [x] SDK bridge architecture
- [x] JVM lifecycle management
- [x] UNV parser integration with fallback
- [x] Setup automation script

### 🚧 In Progress
- [ ] Complete `UNVParser._open_universe()` implementation
- [ ] Verify SDK class names (depends on actual JAR contents)
- [ ] Test with real UNV files

### 📋 Next Steps
1. Run Windows installer to get JARs
2. Inspect JAR contents to find exact class names
3. Complete SDK method calls in `sdk_bridge.py`
4. Test with customer UNV files
5. Deploy to production

## Troubleshooting

### "SDK directory not found"
```bash
# Check SDK location
ls -la backend/app/engines/bobj2sac/sdk/BOBJ_SDK

# If missing, copy from Windows
mv ~/Desktop/BOBJ_SDK backend/app/engines/bobj2sac/sdk/
```

### "Java not found"
```bash
# Install Java
brew install openjdk@11

# Add to PATH
export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"
```

### "JVM failed to start"
```bash
# Check Java version
java -version

# Should see: openjdk version "11.x.x"

# Test JPype
python3 -c "import jpype; print(jpype.__version__)"
```

### "SDK classes not found"
This means we need to inspect the JAR files to find the correct class names:
```bash
# List classes in JAR
jar tf backend/app/engines/bobj2sac/sdk/BOBJ_SDK/java/lib/universe.jar | grep ".class"
```

## Production Deployment

Once SDK is working locally:

1. **Package SDK with application:**
   ```bash
   git add backend/app/engines/bobj2sac/sdk/
   git commit -m "Add SAP BOBJ SDK for UNV parsing"
   ```

2. **Update Render deployment:**
   - Add Java buildpack
   - Install JPype in requirements.txt
   - SDK JARs deploy with code

3. **Test on production:**
   ```bash
   curl -X POST https://migration-studio-api.onrender.com/api/upload \
     -F "file=@universe.unv"
   ```

## License Note

⚠️ **SAP BusinessObjects SDK is proprietary software**
- Licensed by SAP
- Only use with valid SAP licenses
- Not included in this repository
- Users must obtain SDK from SAP downloads

## Support

For SDK-related issues:
- Check SAP SDK documentation
- Verify SDK version compatibility
- Ensure valid SAP license

For integration issues:
- Check logs in `backend/logs/`
- Enable debug logging: `LOG_LEVEL=DEBUG`
- Test JVM startup separately
