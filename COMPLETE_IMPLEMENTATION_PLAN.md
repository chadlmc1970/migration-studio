# Complete BOBJ Migration Tool Implementation Plan
## Multi-Engine Architecture with All Parsers & Generators

**Date:** 2026-03-04
**Status:** Implementation In Progress
**Deployment:** Render (Backend) + Neon (Database) + GitHub Auto-Deploy

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOBJ MIGRATION PIPELINE                       │
│                                                                  │
│  Input: .unx, .unv, .wid, .rpt, .rep, .car files               │
│  Output: SAC models, Datasphere SQL, HANA schemas               │
│  Validation: Correctness, completeness, deployability           │
└─────────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE 1: Parser Engine (bobj2sac)                             │
├─────────────────────────────────────────────────────────────────┤
│  Input Parsers (7 total):                                       │
│  1. ✅ unx.py      - UNX universes (ZIP-based)                  │
│  2. ⚠️ unv.py      - UNV universes (binary) - ENHANCE           │
│  3. ⚠️ wid.py      - WebI documents - NEW                       │
│  4. ⚠️ rpt.py      - Crystal Reports - NEW                      │
│  5. ⚠️ rep.py      - WebI reports (old format) - NEW            │
│  6. ⚠️ car.py      - BIAR archives - NEW                        │
│  7. ⚠️ cms.py      - CMS repository - NEW (optional)            │
│                                                                  │
│  Output: /pipeline/cim/<universe_id>.cim.json                   │
└─────────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE 2: Transformation Engine (cim_transform)                │
├─────────────────────────────────────────────────────────────────┤
│  Output Generators (3-4 total):                                 │
│  8. ⚠️ sac.py           - SAC models - NEW                      │
│  9. ⚠️ sac_story.py     - SAC stories/dashboards - NEW (opt)    │
│  10. ⚠️ datasphere.py   - Datasphere SQL views - NEW            │
│  11. ⚠️ hana.py         - HANA schemas/calc views - NEW         │
│                                                                  │
│  Output: /pipeline/targets/<universe_id>/                       │
│    ├─ sac/model.json                                            │
│    ├─ datasphere/views.sql                                      │
│    └─ hana/schema.sql                                           │
└─────────────────────────────────────────────────────────────────┘

                              ↓

┌─────────────────────────────────────────────────────────────────┐
│  CLAUDE 5: Validation Engine (validation_engine)                │
├─────────────────────────────────────────────────────────────────┤
│  Validation Checks:                                             │
│  - SAC model validation (schema, references)                    │
│  - Datasphere SQL validation (syntax, tables)                   │
│  - HANA schema validation (types, keys)                         │
│  - Cross-artifact consistency                                   │
│  - CIM fidelity (no data loss)                                  │
│                                                                  │
│  Output: /pipeline/validation/<universe_id>/                    │
│    ├─ coverage_report.json                                      │
│    ├─ semantic_diff.json                                        │
│    └─ lineage_graph.dot                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### **Total: 10-11 Parsers/Generators + 1 Validation Engine**

| # | Component | Type | Status | Priority | Location |
|---|-----------|------|--------|----------|----------|
| 1 | UNX Parser | Input | ✅ Exists | - | `backend/app/engines/bobj2sac/io/unx.py` |
| 2 | UNV Parser | Input | ⚠️ Enhance | High | `backend/app/engines/bobj2sac/io/unv.py` |
| 3 | WebI Document Parser | Input | ⚠️ New | **CRITICAL** | `backend/app/engines/bobj2sac/io/wid.py` |
| 4 | Crystal Reports Parser | Input | ⚠️ New | High | `backend/app/engines/bobj2sac/io/rpt.py` |
| 5 | WebI Report Parser | Input | ⚠️ New | Medium | `backend/app/engines/bobj2sac/io/rep.py` |
| 6 | BIAR Archive Parser | Input | ⚠️ New | Medium | `backend/app/engines/bobj2sac/io/car.py` |
| 7 | CMS Repository Parser | Input | ⚠️ New | Low | `backend/app/engines/bobj2sac/io/cms.py` |
| 8 | SAC Model Generator | Output | ⚠️ New | **CRITICAL** | `backend/app/engines/cim_transform/generators/sac.py` |
| 9 | SAC Story Generator | Output | ⚠️ New | Medium | `backend/app/engines/cim_transform/generators/sac_story.py` |
| 10 | Datasphere Generator | Output | ⚠️ New | High | `backend/app/engines/cim_transform/generators/datasphere.py` |
| 11 | HANA Generator | Output | ⚠️ New | High | `backend/app/engines/cim_transform/generators/hana.py` |
| 12 | Validation Engine | Validator | ⚠️ New | **CRITICAL** | `backend/app/engines/validation_engine/` |

---

## Implementation Phases

### **Phase 1: Core Input Parsers (Week 1-2)**
**Priority: Complete WebI parsing - most common format**

#### 1.1 WebI Document Parser (wid.py) - CRITICAL
- **Input:** `.wid` files (ZIP archive containing XML)
- **Output:** CIM with queries, filters, variables, report structure
- **Key Tasks:**
  - Extract ZIP contents
  - Parse `document.xml` for report structure
  - Parse queries and data providers
  - Extract dimensions, measures, filters
  - Map to CIM format

#### 1.2 Enhance UNV Parser (unv.py)
- **Current:** Placeholder only
- **Needed:** Binary format parsing or SAP SDK integration
- **Options:**
  - Use SAP BusinessObjects SDK (if available)
  - Reverse engineer binary format
  - Use metadata companion JSON files

#### 1.3 BIAR Archive Parser (car.py)
- **Input:** `.car` files (BIAR archives - ZIP containing multiple BOBJ objects)
- **Output:** Extract universes, reports, connections
- **Key Tasks:**
  - Extract archive
  - Identify contained objects
  - Route to appropriate parsers (UNX/UNV/WID/RPT)

### **Phase 2: Output Generators (Week 2-3)**
**Priority: SAC model generation first**

#### 2.1 SAC Model Generator (sac.py) - CRITICAL
- **Input:** CIM JSON
- **Output:** `sac/model.json` (SAC semantic model)
- **Structure:**
  ```json
  {
    "modelId": "...",
    "dimensions": [...],
    "measures": [...],
    "relationships": [...],
    "dataSources": [...]
  }
  ```
- **Mapping:**
  - CIM tables → SAC data sources
  - CIM dimensions → SAC dimensions
  - CIM measures → SAC measures
  - CIM joins → SAC relationships

#### 2.2 HANA Schema Generator (hana.py)
- **Input:** CIM JSON
- **Output:**
  - `hana/schema.sql` (DDL for tables)
  - `hana/calculation_views/*.hdbcalculationview` (XML calc views)
- **Generate:**
  - CREATE TABLE statements
  - Primary keys, foreign keys
  - Calculation views for aggregations

#### 2.3 Datasphere Generator (datasphere.py)
- **Input:** CIM JSON
- **Output:** `datasphere/views.sql`
- **Generate:**
  - SQL views matching universe structure
  - Table references
  - Join logic

### **Phase 3: Validation Engine (Week 3-4)**
**Priority: CRITICAL - ensures quality**

#### 3.1 Core Validation Logic
- **SAC Validation:**
  - Valid JSON schema
  - All dimensions reference valid sources
  - All measures have aggregations
  - Relationships are bidirectional

- **HANA Validation:**
  - SQL syntax correctness
  - Data type validity
  - Primary key definitions

- **Datasphere Validation:**
  - SQL syntax
  - Table existence in CIM
  - Join correctness

#### 3.2 Cross-Artifact Validation
- SAC references match HANA tables
- No orphaned dimensions/measures
- CIM fidelity (no data loss)

#### 3.3 Report Generation
- Coverage report (% of CIM represented)
- Semantic diff (CIM vs targets)
- Lineage graph (DOT format)

### **Phase 4: Secondary Input Parsers (Week 4-5)**

#### 4.1 Crystal Reports Parser (rpt.py)
- **Input:** `.rpt` files (Crystal Reports binary)
- **Challenge:** Proprietary binary format
- **Options:**
  - Crystal Reports SDK
  - Third-party libraries
  - Extract via Crystal Server API

#### 4.2 WebI Report Parser (rep.py)
- **Input:** `.rep` files (older WebI format)
- **Similar to:** `.wid` but different XML schema

#### 4.3 CMS Repository Parser (cms.py)
- **Input:** Direct CMS database connection or API
- **Extract:** Universe metadata, report catalog
- **Output:** Batch CIM files

### **Phase 5: Integration & Frontend (Week 5-6)**

#### 5.1 Database Schema Updates (Neon)
```sql
-- Add to universes table
ALTER TABLE universes ADD COLUMN source_format VARCHAR(10);
ALTER TABLE universes ADD COLUMN source_subtype VARCHAR(50);
ALTER TABLE universes ADD COLUMN target_formats JSONB;
ALTER TABLE universes ADD COLUMN parser_version VARCHAR(20);
ALTER TABLE universes ADD COLUMN generator_version VARCHAR(20);

-- Add artifacts table
CREATE TABLE artifacts (
  id SERIAL PRIMARY KEY,
  universe_id VARCHAR(255) REFERENCES universes(id),
  artifact_type VARCHAR(50), -- 'sac_model', 'hana_schema', etc.
  file_path TEXT,
  size_bytes INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### 5.2 API Updates (routes.py)
- Update `/api/upload` - accept all file types
- Add `/api/universes/{id}/configure` - select target formats
- Update `/api/universes/{id}/download` - all artifact types
- Add `/api/parsers` - list available parsers
- Add `/api/generators` - list available generators

#### 5.3 Frontend Updates
- **UploadPage:** Support all file types with icons
- **ConfigurationPage:** Checkbox selector for target formats
- **UniverseDetails:** Display parser/generator used
- **DownloadSection:** Show all available artifacts

### **Phase 6: Testing & Deployment (Week 6)**

#### 6.1 Test Data
- Sample `.unx` universe ✅ exists
- Sample `.wid` WebI document ⚠️ need
- Sample `.rpt` Crystal Report ⚠️ need
- Sample `.car` BIAR archive ⚠️ need

#### 6.2 End-to-End Tests
- Upload each file type
- Run pipeline
- Verify CIM generation
- Verify target generation
- Verify validation reports

#### 6.3 Production Deployment
```bash
# Commit and push
git add .
git commit -m "feat: Complete parser/generator/validator implementation"
git push github main && git push origin main

# Render auto-deploys
# ✅ Backend: https://catchweight-api.onrender.com
# ✅ Frontend: https://catchweight-dashboard.onrender.com
```

---

## File Structure After Implementation

```
migration_studio/
├── backend/
│   ├── app/
│   │   ├── engines/
│   │   │   ├── bobj2sac/           # CLAUDE 1: Parser Engine
│   │   │   │   ├── io/
│   │   │   │   │   ├── detect.py  # ✏️ UPDATE - add new formats
│   │   │   │   │   ├── unx.py     # ✅ EXISTS
│   │   │   │   │   ├── unv.py     # ✏️ ENHANCE
│   │   │   │   │   ├── wid.py     # ⚠️ NEW - WebI documents
│   │   │   │   │   ├── rpt.py     # ⚠️ NEW - Crystal Reports
│   │   │   │   │   ├── rep.py     # ⚠️ NEW - WebI reports (old)
│   │   │   │   │   ├── car.py     # ⚠️ NEW - BIAR archives
│   │   │   │   │   └── cms.py     # ⚠️ NEW - CMS repository
│   │   │   │   └── model/
│   │   │   │       └── cim.py     # ✏️ UPDATE - extend schema
│   │   │   │
│   │   │   ├── cim_transform/      # CLAUDE 2: Transform Engine
│   │   │   │   ├── generators/     # ⚠️ NEW DIRECTORY
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── sac.py     # ⚠️ NEW - SAC models
│   │   │   │   │   ├── sac_story.py # ⚠️ NEW - SAC stories
│   │   │   │   │   ├── datasphere.py # ⚠️ NEW - Datasphere SQL
│   │   │   │   │   └── hana.py    # ⚠️ NEW - HANA schemas
│   │   │   │   └── transform.py   # ✏️ UPDATE - call generators
│   │   │   │
│   │   │   └── validation_engine/  # CLAUDE 5: Validation Engine
│   │   │       ├── __init__.py
│   │   │       ├── cli.py         # ⚠️ NEW - validation-engine CLI
│   │   │       ├── validators/    # ⚠️ NEW
│   │   │       │   ├── sac_validator.py
│   │   │       │   ├── datasphere_validator.py
│   │   │       │   ├── hana_validator.py
│   │   │       │   └── cross_validator.py
│   │   │       ├── reports/       # ⚠️ NEW
│   │   │       │   ├── coverage.py
│   │   │       │   ├── semantic_diff.py
│   │   │       │   └── lineage.py
│   │   │       └── state.py       # ⚠️ NEW - state management
│   │   │
│   │   ├── api/
│   │   │   └── routes.py          # ✏️ UPDATE - new endpoints
│   │   ├── models/
│   │   │   ├── database.py        # ✏️ UPDATE - new columns
│   │   │   └── schemas.py         # ✏️ UPDATE - new schemas
│   │   └── services/
│   │       └── pipeline_integrated.py # ✏️ UPDATE - orchestrate all
│   │
│   ├── schema.sql                 # ✏️ UPDATE - new tables/columns
│   └── requirements.txt           # ✏️ UPDATE - new dependencies
│
└── frontend/
    ├── components/
    │   ├── UploadPage.tsx         # ✏️ UPDATE - all file types
    │   ├── ConfigPage.tsx         # ⚠️ NEW - target format selector
    │   ├── UniverseDetails.tsx    # ✏️ UPDATE - show artifacts
    │   └── DownloadSection.tsx    # ✏️ UPDATE - all downloads
    └── app/
        └── page.tsx               # ✏️ UPDATE - integrate new pages
```

---

## Dependencies to Add

### Backend (requirements.txt)
```
# Existing
fastapi
sqlalchemy
psycopg2-binary
pydantic

# New for parsers
lxml>=4.9.0           # XML parsing for WID/UNX
zipfile36>=0.1.3      # Enhanced ZIP handling
sqlparse>=0.4.4       # SQL validation
jsonschema>=4.17.0    # JSON schema validation

# New for Crystal Reports (if using SDK)
# comtypes>=1.1.14    # Windows COM for Crystal SDK
# pythoncom>=0.0.1    # Windows-specific

# New for validation
networkx>=3.0         # Lineage graph generation
graphviz>=0.20        # DOT file generation
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "@monaco-editor/react": "^4.5.0",  // Code viewer for SQL/JSON
    "react-syntax-highlighter": "^15.5.0",  // Syntax highlighting
    "vis-network": "^9.1.6"  // Lineage graph visualization
  }
}
```

---

## Success Metrics

### Phase 1-2 Complete:
- ✅ Upload .wid, .rpt, .car files
- ✅ Generate SAC models, HANA schemas, Datasphere SQL
- ✅ Download all artifacts

### Phase 3 Complete:
- ✅ Validation reports show coverage %
- ✅ Semantic diff highlights transformations
- ✅ Lineage graph visualizes data flow

### Phase 4-6 Complete:
- ✅ All 11 parsers/generators operational
- ✅ End-to-end pipeline tested
- ✅ Deployed to production
- ✅ Documentation complete

---

## Next Steps

1. **Start with Phase 1.1:** Implement WebI Document Parser (wid.py)
2. **Then Phase 2.1:** Implement SAC Model Generator (sac.py)
3. **Then Phase 3:** Implement Validation Engine
4. **Iterate through remaining parsers/generators**

---

**Owner:** Claude Code (All 3 personas: Claude 1, 2, 5)
**Deployment Target:** Render + Neon
**Git Remote:** github → https://github.com/chadlmc1970/CatchWeight.git
**Auto-Deploy Branch:** main
