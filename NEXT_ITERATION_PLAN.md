# Migration Studio: Next Iteration Plan
## SDK-as-a-Service Architecture

**Date**: March 5, 2026
**Version**: 2.0
**Status**: Planning Phase
**Priority**: High - Unblocks eFashion and future binary universes

---

## Executive Summary

**Current State**: Migration Studio successfully processes BOEXI universes with AI-powered semantic enhancements, but faces a critical deployment blocker: the SAP BusinessObjects SDK (1.6GB of Java JARs) cannot be deployed to Render's ephemeral filesystem.

**Problem**: eFashion.unx generates empty output because the SDK is unavailable in production, despite having functional SDK integration code.

**Solution**: Extract SDK functionality into a dedicated microservice with persistent storage, enabling SDK-based parsing for all binary universes without deployment constraints.

**Expected Impact**:
- ✅ Unblocks eFashion and all future .unx/.unv universes
- ✅ Enables horizontal scaling of SDK parsing
- ✅ Reduces main app footprint (1.6GB → ~50MB)
- ✅ Reusable across multiple projects/teams
- ✅ Single SDK deployment point

---

## Current Architecture (V1.0)

```
┌─────────────────────────────────────────────────────────┐
│ Migration Studio Backend (FastAPI)                      │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ BOBJ Universe Upload (.unx/.unv)                │   │
│  └────────────────┬────────────────────────────────┘   │
│                   ↓                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Binary Parser (binary.py)                       │   │
│  │  • Try SDK parsing (sdk_bridge.py)              │   │
│  │  • Fall back to Properties extraction           │   │
│  │  • Fall back to companion JSON                  │   │
│  └────────────────┬────────────────────────────────┘   │
│                   ↓                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SDK Bridge (JPype + SAP JARs)                   │   │
│  │  ❌ Problem: 1.6GB JARs not on Render          │   │
│  │  ❌ Result: SDK_AVAILABLE = False               │   │
│  └─────────────────────────────────────────────────┘   │
│                   ↓                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ AI Semantic Enhancer (Claude API)               │   │
│  │  ✅ Formula translation                          │   │
│  │  ✅ Hierarchy detection                          │   │
│  │  ✅ Dimension classification                     │   │
│  └────────────────┬────────────────────────────────┘   │
│                   ↓                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Target Generators (SAC, Datasphere, HANA)       │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Current Deployment**:
- Frontend: https://migration-studio.onrender.com (Next.js static site)
- Backend: https://migration-studio-api.onrender.com (FastAPI, ephemeral filesystem)
- Database: Neon PostgreSQL
- SDK Status: ❌ Not deployed, causing empty eFashion output

---

## Proposed Architecture (V2.0)

```
┌────────────────────────────────────────────────────────────────────┐
│ Migration Studio Backend (FastAPI)                                 │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Binary Parser (binary.py)                                   │  │
│  │  1. Check if SDK service available                          │  │
│  │  2. If yes → HTTP POST to SDK service                       │  │
│  │  3. If no → Fall back to Properties extraction              │  │
│  └───────────────────────┬─────────────────────────────────────┘  │
│                          │                                          │
└──────────────────────────┼──────────────────────────────────────────┘
                           │ HTTP REST API
                           ↓
┌────────────────────────────────────────────────────────────────────┐
│ SDK Service (Java Spring Boot) - NEW MICROSERVICE                  │
│ Port: 8080                                                          │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ REST API Endpoints                                          │  │
│  │  POST /api/parse-universe                                   │  │
│  │  GET  /api/health                                           │  │
│  │  GET  /api/sdk-version                                      │  │
│  └───────────────────────┬─────────────────────────────────────┘  │
│                          ↓                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Universe Parser (Java)                                      │  │
│  │  • Load .unx/.unv file from multipart upload                │  │
│  │  • Use SAP BusinessObjects SDK                              │  │
│  │  • Extract tables, joins, dimensions, measures              │  │
│  │  • Return JSON response                                     │  │
│  └───────────────────────┬─────────────────────────────────────┘  │
│                          ↓                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ SAP BOBJ SDK (1.6GB JARs) - Persistent Disk                │  │
│  │  /app/sdk/BOBJ_SDK/                                         │  │
│  │  • businessobjects.jar                                      │  │
│  │  • celib.jar                                                │  │
│  │  • unv_*.jar (universe parsers)                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
        Deployed on Render with Persistent Disk (5GB)
```

**Benefits**:
1. **Separation of Concerns**: SDK complexity isolated from main app
2. **Independent Scaling**: Scale SDK service independently based on parsing load
3. **Persistent Storage**: Render Persistent Disk keeps SDK JARs across deploys
4. **Reusability**: Other projects can use the SDK service via REST API
5. **Single Deployment**: One SDK instance serves multiple consumers
6. **Language-Appropriate**: Java for SDK, Python for business logic

---

## Implementation Plan

### Phase 1: SDK Service Foundation (Week 1)

**Step 1.1**: Create Java Spring Boot project structure
```
sdk-service/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/migrationstudio/sdk/
│       │       ├── SdkServiceApplication.java
│       │       ├── controller/
│       │       │   ├── ParserController.java
│       │       │   └── HealthController.java
│       │       ├── service/
│       │       │   ├── UniverseParserService.java
│       │       │   └── SdkLoaderService.java
│       │       └── model/
│       │           ├── UniverseParseRequest.java
│       │           └── UniverseParseResponse.java
│       └── resources/
│           └── application.properties
├── pom.xml
├── Dockerfile
└── render.yaml
```

**Step 1.2**: Implement REST API endpoints

**Endpoint 1: Parse Universe**
```java
POST /api/parse-universe
Content-Type: multipart/form-data

Request:
- file: .unx or .unv file (multipart upload)

Response (JSON):
{
  "success": true,
  "universe": {
    "name": "eFashion",
    "version": "4.3",
    "description": "Fashion industry analytics"
  },
  "tables": [
    {"name": "PRODUCT", "type": "Table", "sql": "SELECT * FROM PRODUCT"},
    {"name": "SALES_FACT", "type": "Table", "sql": "SELECT * FROM SALES"}
  ],
  "joins": [
    {
      "left_table": "SALES_FACT",
      "right_table": "PRODUCT",
      "left_column": "PRODUCT_ID",
      "right_column": "PRODUCT_ID",
      "condition": "SALES_FACT.PRODUCT_ID = PRODUCT.PRODUCT_ID"
    }
  ],
  "dimensions": [
    {
      "name": "Product Name",
      "table": "PRODUCT",
      "column": "PRODUCT_NAME",
      "data_type": "VARCHAR",
      "description": "Product name dimension"
    }
  ],
  "measures": [
    {
      "name": "Revenue",
      "table": "SALES_FACT",
      "column": "REVENUE",
      "aggregation": "SUM",
      "formula": "SUM(SALES_FACT.REVENUE)"
    }
  ],
  "contexts": [...],
  "prompts": [...],
  "connection": {...}
}
```

**Endpoint 2: Health Check**
```java
GET /api/health

Response:
{
  "status": "healthy",
  "sdk_version": "4.3",
  "sdk_loaded": true,
  "uptime_seconds": 3600
}
```

**Step 1.3**: SDK loader service
```java
@Service
public class SdkLoaderService {
    private static final String SDK_DIR = "/app/sdk/BOBJ_SDK/";

    @PostConstruct
    public void loadSdk() {
        // Load all JARs from SDK directory
        File sdkDir = new File(SDK_DIR);
        File[] jars = sdkDir.listFiles((dir, name) -> name.endsWith(".jar"));

        for (File jar : jars) {
            // Add to classpath dynamically
            URLClassLoader classLoader = (URLClassLoader) ClassLoader.getSystemClassLoader();
            Method method = URLClassLoader.class.getDeclaredMethod("addURL", URL.class);
            method.setAccessible(true);
            method.invoke(classLoader, jar.toURI().toURL());
        }

        log.info("Loaded {} SDK JARs from {}", jars.length, SDK_DIR);
    }
}
```

**Step 1.4**: Universe parser service (port existing sdk_bridge.py logic)
```java
@Service
public class UniverseParserService {
    public UniverseParseResponse parseUniverse(MultipartFile file) {
        // Save file to temp location
        Path tempFile = Files.createTempFile("universe-", ".unx");
        file.transferTo(tempFile.toFile());

        // Load universe using BOBJ SDK
        Universe universe = UniverseFactory.loadUniverse(tempFile.toString());

        // Extract metadata
        UniverseParseResponse response = new UniverseParseResponse();
        response.setUniverse(extractUniverseMetadata(universe));
        response.setTables(extractTables(universe));
        response.setJoins(extractJoins(universe));
        response.setDimensions(extractDimensions(universe));
        response.setMeasures(extractMeasures(universe));
        response.setContexts(extractContexts(universe));
        response.setPrompts(extractPrompts(universe));
        response.setConnection(extractConnection(universe));

        return response;
    }
}
```

---

### Phase 2: Deployment Configuration (Week 1-2)

**Step 2.1**: Create Dockerfile for SDK service
```dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

# Copy Spring Boot JAR
COPY target/sdk-service-1.0.0.jar /app/sdk-service.jar

# SDK will be mounted via Render Persistent Disk
VOLUME /app/sdk

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "/app/sdk-service.jar"]
```

**Step 2.2**: Create render.yaml for SDK service
```yaml
services:
  - type: web
    name: migration-studio-sdk
    env: docker
    dockerfilePath: ./Dockerfile
    plan: starter  # $7/month
    healthCheckPath: /api/health
    envVars:
      - key: SERVER_PORT
        value: 8080
      - key: SDK_DIR
        value: /app/sdk/BOBJ_SDK
    disk:
      name: sdk-storage
      mountPath: /app/sdk
      sizeGB: 5
```

**Step 2.3**: Upload SDK to Render Persistent Disk

Option A: **SCP Upload** (if Render Shell available)
```bash
# Compress SDK locally
cd /Users/I870089/migration_studio/backend/app/engines/bobj2sac/sdk/
tar -czf BOBJ_SDK.tar.gz BOBJ_SDK/

# Upload to Render
render ssh migration-studio-sdk
mkdir -p /app/sdk
scp BOBJ_SDK.tar.gz render:/app/sdk/
tar -xzf /app/sdk/BOBJ_SDK.tar.gz -C /app/sdk/
```

Option B: **Initial Deploy with SDK** (recommended)
```bash
# Include SDK in Docker image for first deploy only
# Then persist to disk and remove from image
COPY sdk/BOBJ_SDK /app/sdk/BOBJ_SDK
```

---

### Phase 3: Backend Integration (Week 2)

**Step 3.1**: Update binary.py to use SDK service

**File**: `backend/app/engines/bobj2sac/io/binary.py`

**Changes**:
```python
import requests
from app.config import SDK_SERVICE_URL, SDK_SERVICE_TIMEOUT

def extract_binary_universe(input_path: Path, output_dir: Path, logger: ConversionLogger) -> CanonicalModel:
    logger.log(f"Extracting binary universe: {input_path}")

    # Read source file
    with open(input_path, "rb") as f:
        data = f.read()

    source_file = SourceFile(
        relative_path=input_path.name,
        size_bytes=len(data),
        sha256=sha256_bytes(data),
    )

    cim = CanonicalModel(
        universe_id=input_path.stem,
        universe_name=input_path.stem,
        source_format="unx_binary",
        source_files=[source_file],
    )

    # Try SDK service first (HTTP-based)
    if SDK_SERVICE_URL:
        try:
            logger.log(f"Using remote SDK service: {SDK_SERVICE_URL}")
            cim_data = _call_sdk_service(input_path, logger)
            _populate_cim_from_sdk(cim, cim_data, logger)

            cim.update_counts()
            logger.log(f"SDK service extraction complete: {len(cim.data_foundation.tables)} tables")
            return cim

        except Exception as e:
            logger.warn(f"SDK service failed: {e} - falling back to manual extraction")
    else:
        logger.warn("SDK service not configured - using fallback extraction methods")

    # Fallback: Properties file extraction...
    # (existing fallback code)


def _call_sdk_service(input_path: Path, logger: ConversionLogger) -> dict:
    """Call remote SDK service to parse universe."""
    with open(input_path, "rb") as f:
        files = {"file": (input_path.name, f, "application/octet-stream")}

        response = requests.post(
            f"{SDK_SERVICE_URL}/api/parse-universe",
            files=files,
            timeout=SDK_SERVICE_TIMEOUT
        )

        response.raise_for_status()
        return response.json()
```

**Step 3.2**: Update config.py with SDK service settings

**File**: `backend/app/config.py`

**Add**:
```python
# SDK Service Configuration
SDK_SERVICE_URL = os.getenv("SDK_SERVICE_URL", "")  # e.g., https://migration-studio-sdk.onrender.com
SDK_SERVICE_TIMEOUT = int(os.getenv("SDK_SERVICE_TIMEOUT", "60"))  # 60 seconds
```

**Step 3.3**: Update .env.example

**File**: `backend/.env.example`

**Add**:
```
# SDK Service (for binary universe parsing)
SDK_SERVICE_URL=https://migration-studio-sdk.onrender.com
SDK_SERVICE_TIMEOUT=60
```

**Step 3.4**: Add requests dependency

**File**: `backend/requirements.txt`

**Add**:
```
requests>=2.31.0
```

---

### Phase 4: Testing & Validation (Week 2-3)

**Test Case 1: SDK Service Standalone**
```bash
# Test with eFashion locally
curl -X POST http://localhost:8080/api/parse-universe \
  -F "file=@/path/to/eFashion.unx" \
  | jq .
```

**Test Case 2: Backend Integration (Local)**
```bash
# Set SDK_SERVICE_URL to local SDK service
export SDK_SERVICE_URL=http://localhost:8080

# Upload eFashion via Migration Studio UI
# Verify CIM has tables, dimensions, measures
```

**Test Case 3: Production Deployment**
```bash
# Add SDK_SERVICE_URL to Render environment
SDK_SERVICE_URL=https://migration-studio-sdk.onrender.com

# Re-upload eFashion.unx
# Check logs for "Using remote SDK service"
# Verify SAC model has content
```

**Success Criteria**:
- ✅ SDK service returns JSON with 10+ tables for eFashion
- ✅ Backend successfully calls SDK service and populates CIM
- ✅ eFashion SAC model has dimensions, measures, joins
- ✅ SDK service responds in <5 seconds for typical universe
- ✅ Health check endpoint returns healthy status

---

### Phase 5: Optimization & Monitoring (Week 3-4)

**Step 5.1**: Add caching to SDK service
```java
@Service
public class UniverseParserService {
    @Cacheable(value = "parsedUniverses", key = "#file.originalFilename")
    public UniverseParseResponse parseUniverse(MultipartFile file) {
        // Parsing logic...
    }
}
```

**Step 5.2**: Add metrics endpoint
```java
GET /api/metrics

Response:
{
  "total_parses": 42,
  "avg_parse_time_ms": 2340,
  "cache_hit_rate": 0.65,
  "uptime_seconds": 86400
}
```

**Step 5.3**: Add request logging
```java
@Slf4j
@Component
public class RequestLoggingFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        long start = System.currentTimeMillis();
        chain.doFilter(request, response);
        long elapsed = System.currentTimeMillis() - start;

        log.info("Request: {} - {}ms", ((HttpServletRequest) request).getRequestURI(), elapsed);
    }
}
```

**Step 5.4**: Monitor Render logs
```bash
render logs migration-studio-sdk --tail
```

---

## Cost Analysis

### Current State (V1.0)
- Backend (Starter): $7/month
- Frontend (Static): $0/month
- Database (Neon Free): $0/month
- **Total**: $7/month

### With SDK Service (V2.0)
- Backend (Starter): $7/month
- SDK Service (Starter + 5GB Disk): $7 + $1 = $8/month
- Frontend (Static): $0/month
- Database (Neon Free): $0/month
- **Total**: $15/month

**Cost Increase**: +$8/month ($96/year)

**Value**:
- Unblocks all binary universes (eFashion + future .unx files)
- Enables SDK reuse across multiple projects
- Independent scaling for parse-heavy workloads
- Cleaner architecture

**ROI**: High - solves critical blocker, minimal cost

---

## Deployment Sequence

### Step-by-Step Rollout

**Day 1-2: SDK Service Setup**
1. Create Java Spring Boot project
2. Implement /api/parse-universe endpoint
3. Port sdk_bridge.py logic to Java
4. Test locally with eFashion.unx

**Day 3-4: Render Deployment**
1. Create Dockerfile and render.yaml
2. Deploy SDK service to Render
3. Configure Persistent Disk (5GB)
4. Upload BOBJ_SDK.tar.gz to disk

**Day 5-6: Backend Integration**
1. Update binary.py to call SDK service
2. Add SDK_SERVICE_URL to config
3. Add requests dependency
4. Test integration locally

**Day 7: Production Deployment**
1. Push backend changes to GitHub
2. Add SDK_SERVICE_URL to Render backend env
3. Test with eFashion upload
4. Verify logs and output

**Day 8-14: Monitoring & Optimization**
1. Monitor SDK service logs
2. Add caching for repeat parses
3. Add metrics endpoint
4. Document API for future consumers

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| eFashion tables extracted | >10 tables | CIM JSON inspection |
| eFashion dimensions | >20 dimensions | SAC model output |
| SDK parse time | <5 seconds | Render logs |
| Service uptime | >99% | Health check monitoring |
| Cache hit rate | >50% | Metrics endpoint |
| API response time | <10 seconds | Backend logs |

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| SDK service unavailable | High | Fallback to Properties extraction (existing) |
| Persistent disk full | Medium | Monitor disk usage, increase to 10GB if needed |
| Java memory issues | Medium | Set JVM heap size: `-Xmx2G -Xms512M` |
| SDK license issues | Low | SDK already owned, service is internal use only |
| Render cold starts | Low | Keep service warm with health check pings |

---

## Alternative Approaches Considered

### Option 1: Deploy SDK JARs with Backend (Current V1.0)
**Pros**: Simple, no microservice needed
**Cons**: ❌ 1.6GB doesn't fit ephemeral storage, ❌ bloats main app
**Decision**: Rejected - not feasible on Render

### Option 2: Use Render Persistent Disk on Backend
**Pros**: Single service
**Cons**: ❌ Persistent disk only on paid tiers, ❌ mixes concerns
**Decision**: Rejected - violates separation of concerns

### Option 3: SDK-as-a-Service Microservice (Proposed V2.0) ✅
**Pros**: ✅ Persistent disk, ✅ independent scaling, ✅ reusable
**Cons**: Additional service to maintain
**Decision**: **SELECTED** - best long-term architecture

### Option 4: Cloud Storage (S3/GCS) for SDK
**Pros**: Simple storage
**Cons**: ❌ Still need to load 1.6GB on startup, ❌ cold start penalty
**Decision**: Rejected - doesn't solve root problem

---

## Next Steps After Approval

1. ✅ Review and approve this plan
2. Create Java Spring Boot project skeleton
3. Port sdk_bridge.py logic to Java
4. Create Dockerfile and render.yaml
5. Deploy SDK service to Render
6. Update backend binary.py integration
7. Test with eFashion.unx
8. Monitor and optimize

---

## Open Questions

1. **SDK License**: Confirm SDK can be deployed to cloud service (internal use only)
2. **Java Version**: Confirm Java 17 is compatible with BOBJ SDK
3. **Render Plan**: Starter plan sufficient or need Standard for better performance?
4. **Caching Strategy**: Cache parsed universes by filename or SHA256?
5. **Security**: Add API key authentication for SDK service?

---

## Summary

**Current Problem**: eFashion.unx generates empty output because 1.6GB SDK can't deploy to Render

**Proposed Solution**: SDK-as-a-Service microservice with persistent disk

**Implementation Time**: 1-2 weeks

**Cost**: +$8/month

**Impact**: Unblocks all binary universes, enables SDK reuse, cleaner architecture

**Risk**: Low - fallback mechanisms in place

**Recommendation**: PROCEED with SDK-as-a-Service implementation

---

**Document Version**: 2.0
**Last Updated**: March 5, 2026
**Status**: Ready for Implementation
**Approval Required**: Yes
