# Additional SAP SDK Components Investigation

## Question: What additional SAP SDK components are needed?

### 🎯 KEY DISCOVERY: Multiple SDK Components Required

Our investigation revealed the SAP BusinessObjects SDK has **multiple sub-components** with different requirements:

---

## SDK Components Found

### 1. **Base MDS SDK** (What we were using)
- **Location**: `backend/app/engines/bobj2sac/sdk/BOBJ_SDK/java/lib/`
- **JAR Count**: 383 JARs
- **Java Version**: Java 11 (class version 55.0)
- **Purpose**: Basic universe model (MDS = Metadata Services)
- **Status**: ✅ Works but incomplete for binary deserialization

### 2. **Information Design Tool (IDT) SDK** (The missing piece!)
- **Location**: `backend/app/engines/bobj2sac/sdk/BOBJ_SDK/Information Design Tool/plugins/`
- **JAR Count**: 407 JARs
- **Java Version**: **Java 17 (class version 61.0)** ⚠️
- **Key JARs Found**:
  - `com.businessobjects.mds.resource.jar` ← **ResourceFactory implementations**
  - `com.businessobjects.bimodeler.universe.jar` ← **Universe modeling**
  - `com.businessobjects.universe.migration.jar` ← **Universe migration tools**
- **Status**: ⚠️ Requires Java 17 upgrade

### 3. **Semantic Layer (SL) SDK**
- **Location**: `backend/app/engines/bobj2sac/sdk/BOBJ_SDK/SL SDK/`
- **Status**: Permission issues, not yet tested
- **Purpose**: Semantic layer authoring APIs

---

## The Problem: Java Version Mismatch

```
❌ Error: UnsupportedClassVersionError
   com.businessobjects.mds.universe.UniversePackage compiled with Java 17 (class version 61.0)
   Current runtime: Java 11 (class version 55.0)
```

### What This Means:

The **Information Design Tool SDK JARs require Java 17**, but we're using Java 11.

The base SDK (java/lib) uses Java 11, but the IDT SDK (plugins/) uses Java 17.

---

## Solution Options

### Option A: Upgrade to Java 17 (Recommended)

**Steps**:
1. Install Java 17: `brew install openjdk@17` ✅ **DONE**
2. Update [sdk_bridge.py](backend/app/engines/bobj2sac/sdk_bridge.py) Java path
3. Include BOTH base SDK + IDT SDK JARs (790 total)
4. Re-test with Java 17

**Benefits**:
- Access to `com.businessobjects.mds.resource.jar`
- Complete universe handling APIs
- Migration tools available

**Risks**:
- May still hit encryption/license requirements
- Render needs Java 17 installation

### Option B: Use Only Java 11 Base SDK (Current State)

**Status**: This is what's deployed now (placeholder mode)

**Benefits**:
- Already working on Java 11
- Simpler deployment

**Limitations**:
- Missing ResourceFactory implementations
- Can't load binary .blx/.dfx/.cnx files
- Placeholder metadata only

### Option C: Hybrid Approach

Use base SDK for structure, IDT SDK for specific operations:
- Load with Java 11 base SDK for basic operations
- Switch to Java 17 + IDT for file deserialization
- Requires JVM restart (complex)

---

## What the IDT SDK Might Unlock

If Java 17 + IDT SDK works:

### Potential Benefits:
- `com.businessobjects.mds.resource.jar` contains ResourceFactory
- Could deserialize binary .blx/.dfx/.cnx files
- Access to universe migration APIs
- Full metadata extraction without CMS server

### Still Unknown:
- Whether ResourceFactory can decrypt the proprietary format
- If license/authentication is still required
- If CMS connection is mandatory

---

## Binary Format Investigation

Our testing revealed the binary files (after extraction) have:

**Header**: `04 00 00 00 00 1a 02 01 00 10 00 00 ...`

**Tests Performed**:
- ❌ Standard EMF XMI: "Content not allowed in prolog"
- ❌ EMF Binary: "Invalid signature for binary EMF serialization"
- ❌ Base SDK ResourceFactory: `UnsupportedOperationException`
- ⏳ IDT SDK ResourceFactory: **Blocked by Java version**

---

## Recommendations

### Phase 1 (Current - DEPLOYED) ✅
**Keep placeholder mode with Java 11**
- System is operational
- Users can test pipeline
- No complexity

### Phase 2A (Next - Test Locally)
**Test Java 17 + IDT SDK**
1. ✅ Install Java 17
2. Update sdk_bridge.py to use Java 17
3. Include IDT plugins in classpath
4. Test if `com.businessobjects.mds.resource.jar` can load binary files
5. Document results

### Phase 2B (If Java 17 Works)
**Deploy to Render with Java 17**
1. Update render-build.sh to install Java 17
2. Upload full SDK (1.6GB) to persistent disk
3. Enable real metadata extraction

### Phase 3 (If Still Encrypted)
**Alternative Solutions**
- Contact SAP support for SDK documentation
- Use SAP BOBJ export tool to re-export as XML
- Reverse-engineer binary format
- Use CMS server connection approach

---

## Files Structure

```
backend/app/engines/bobj2sac/sdk/BOBJ_SDK/
├── java/lib/                          ← Java 11, 383 JARs (base SDK)
├── Information Design Tool/plugins/   ← Java 17, 407 JARs ⚠️ (IDT SDK)
├── SL SDK/                            ← Semantic Layer SDK
└── [other components]
```

**Key Insight**: We have the SDK components, but need Java 17 to use them!

---

## Next Action

**Test with Java 17 locally** to see if the IDT SDK ResourceFactory can decrypt the binary files.

```bash
# Already completed:
brew install openjdk@17  ✅

# Next steps:
1. Update sdk_bridge.py with Java 17 path
2. Add IDT plugins to classpath
3. Test binary file loading
4. Report findings
```

---

## Summary

**Additional SDK Components Needed**: ✅ **Already have them!**

The "additional components" are the **Information Design Tool plugins** which are ALREADY in our SDK folder, but require **Java 17** instead of Java 11.

The next breakthrough is testing if Java 17 + IDT SDK can decrypt the binary files, or if we still need CMS/license/authentication.
