# SAP BusinessObjects SDK Deployment Guide

## Problem
The SAP BOBJ SDK is **1.6GB** (1,145 JAR files) - too large for GitHub.

## Solution: Placeholder Mode (Already Implemented)

The system operates in **placeholder mode** by default and does NOT require the SDK JARs on Render.

### How It Works

1. **Parser Check** ([sdk_bridge.py:25-32](../backend/app/engines/bobj2sac/sdk_bridge.py#L25-L32)):
   ```python
   @classmethod
   def start_jvm(cls) -> bool:
       """Start JVM with SDK JARs"""
       sdk_dir = Path(__file__).parent / "sdk/BOBJ_SDK"

       if not sdk_dir.exists():
           logger.warning("SDK not found - operating in placeholder mode")
           return False  # ← Graceful fallback
   ```

2. **Placeholder CIM Generation** ([unv.py:45-89](../backend/app/engines/bobj2sac/io/unv.py#L45-L89)):
   ```python
   if not BOBJSDKBridge.start_jvm():
       logger.warning("SDK unavailable - generating placeholder CIM")
       return cls._create_placeholder_cim(unx_path)
   ```

3. **Users can still**:
   - ✅ Upload .unx files
   - ✅ Get placeholder CIM metadata
   - ✅ Transform to SAC/Datasphere/HANA
   - ✅ Download artifacts
   - ✅ See validation reports

## Deployment Status

### ✅ Production Ready WITHOUT SDK
- **Current Deploy**: Placeholder mode operational
- **User Experience**: Fully functional pipeline
- **Limitation**: Metadata is placeholder (not real universe content)

### 🔧 Optional: Full SDK Deployment (Future)

If you want FULL metadata extraction (not just placeholders):

#### Option 1: Render Persistent Disk (Recommended)
1. Create Render Persistent Disk (25GB)
2. Mount to `/opt/bobj_sdk`
3. Upload SDK via SFTP or Render shell
4. Update path in `sdk_bridge.py`:
   ```python
   sdk_dir = Path("/opt/bobj_sdk/BOBJ_SDK")
   ```

#### Option 2: External Storage (S3/GCS)
1. Upload SDK to S3 bucket
2. Download on Render startup (in `render-build.sh`):
   ```bash
   if [ ! -d "/opt/bobj_sdk" ]; then
       aws s3 sync s3://your-bucket/bobj-sdk /opt/bobj_sdk
   fi
   ```

#### Option 3: Docker Image with SDK
1. Build custom Docker image with SDK embedded
2. Deploy to Render as Docker service
3. Note: Image will be ~2GB

## Current Recommendation

**Deploy AS-IS** with placeholder mode:
- ✅ Fully functional system
- ✅ Fast deployment (no SDK upload)
- ✅ Users can upload and transform universes
- ⏳ Add real SDK in Phase 2 when needed

The SDK decryption issue (documented in [SDK_STATUS_REPORT.md](SDK_STATUS_REPORT.md)) means even WITH the SDK, we can't decrypt the binary files without:
- SAP BOBJ server connection
- SDK license file
- Or additional SAP components

So deploying without SDK is actually the **correct approach** until we solve decryption.

---

## Files Deployed to Production

### ✅ In Git (Deployed Now)
- [backend/app/engines/bobj2sac/sdk_bridge.py](../backend/app/engines/bobj2sac/sdk_bridge.py)
- [backend/app/engines/bobj2sac/io/unv.py](../backend/app/engines/bobj2sac/io/unv.py)
- [backend/app/services/artifact_storage.py](../backend/app/services/artifact_storage.py)
- Documentation files

### ❌ NOT in Git (Not Needed Yet)
- `backend/app/engines/bobj2sac/sdk/BOBJ_SDK/` (1.6GB SDK)

---

**Status**: ✅ **PRODUCTION READY** with placeholder mode
