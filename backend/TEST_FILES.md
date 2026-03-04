# Sample Universe Files for Testing

## Available Test Files

### 1. Mock Test File (Created)
**Location**: `/Users/I870089/test_universe.unv`
**Size**: 316 bytes
**Type**: Text-based mock file
**Purpose**: Quick upload endpoint testing
**Usage**: Upload via API to test validation and file handling

```bash
# Upload mock file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/Users/I870089/test_universe.unv"
```

---

### 2. Real BusinessObjects Sample File
**Location**: `/Users/I870089/BOBJ_SAC_Converter/fixtures/sample.unx`
**Size**: 1.2 KB
**Type**: Real BusinessObjects Universe export
**Purpose**: End-to-end pipeline testing
**Usage**: Upload and run through full pipeline

```bash
# Upload real universe file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/Users/I870089/BOBJ_SAC_Converter/fixtures/sample.unx"
```

---

## Test Results ✅

Both files successfully uploaded to `~/pipeline/input/`:

```bash
$ ls -lh ~/pipeline/input/
total 16
-rw-r--r--  1 I870089  staff   1.2K Mar  4 09:22 sample.unx
-rw-r--r--  1 I870089  staff   316B Mar  4 09:22 test_universe.unv
```

**Upload Endpoint**: ✅ Working
**File Validation**: ✅ Working (rejects non-.unv/.unx files)
**File Storage**: ✅ Files saved to `~/pipeline/input/`

---

## Testing the Full Pipeline

Now that files are uploaded, you can test the complete pipeline:

### Option 1: Run Pipeline via API
```bash
# Execute full pipeline
curl -X POST http://localhost:8000/api/run

# Monitor run status
curl http://localhost:8000/api/runs/active | jq

# Check results
curl http://localhost:8000/api/universes | jq
```

### Option 2: Quick Test Script
```bash
# Run the simple test script
~/test_simple.sh
```

---

## File Format Notes

### .unv Files
- **Format**: BusinessObjects Universe (UNV) binary format
- **Contains**: Metadata, schema definitions, semantic layer
- **Parsed by**: Parser Engine (Claude 1) via `bobj2sac`

### .unx Files
- **Format**: BusinessObjects Universe Export (UNX) format
- **Contains**: Compressed universe data
- **Parsed by**: Parser Engine (Claude 1) via `bobj2sac`

---

## Creating Additional Test Files

If you need more test files:

### Simple Mock File
```bash
# Create a basic mock universe file
cat > ~/my_test.unv << 'EOF'
MOCK_UNIVERSE: my_test
TABLES: customers, orders, products
DIMENSIONS: customer_name, product_name, order_date
MEASURES: revenue, quantity, count
EOF

# Upload it
curl -X POST http://localhost:8000/api/upload \
  -F "file=@~/my_test.unv"
```

### Copy Real Sample
```bash
# Use the existing sample from parser fixtures
cp ~/BOBJ_SAC_Converter/fixtures/sample.unx ~/my_universe.unx

# Upload it
curl -X POST http://localhost:8000/api/upload \
  -F "file=@~/my_universe.unx"
```

---

## Testing File Validation

The upload endpoint validates file extensions:

```bash
# ✅ Valid - .unv extension
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/file.unv"

# ✅ Valid - .unx extension
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/file.unx"

# ❌ Invalid - other extensions rejected
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/file.txt"
# Returns: {"detail": "Only .unv and .unx files are allowed"}
```

---

## Cleanup

To remove test files:

```bash
# Remove uploaded files from pipeline
rm ~/pipeline/input/test_universe.unv
rm ~/pipeline/input/sample.unx

# Remove source test file
rm ~/test_universe.unv

# Remove test scripts
rm ~/test_simple.sh
rm ~/test_upload.sh
```

---

## Integration with Frontend

Your frontend can upload files using FormData:

```typescript
// Frontend upload example
async function uploadUniverse(file: File) {
  const formData = new FormData();
  formData.append('file', file);  // ⚠️ Field name must be 'file'

  const response = await fetch('http://localhost:8000/api/upload', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  console.log('Uploaded:', result.filename);
  console.log('Path:', result.path);
}
```

**Important**: The FormData field name MUST be `"file"` to match the backend endpoint signature.

---

## Next Steps

1. ✅ Files are uploaded
2. ⏭️ Test full pipeline: `POST /api/run`
3. ⏭️ Check validation reports: `GET /api/universes/{id}/reports`
4. ⏭️ Download artifacts: `GET /api/universes/{id}/download?artifact=sac/model.json`

Happy testing! 🚀
