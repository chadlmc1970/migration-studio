#!/usr/bin/env python3
"""
Verify File Extraction and SDK Loading
Test if we can actually open the extracted universe files with SDK
"""
import sys
import os
from pathlib import Path
import zipfile

sys.path.insert(0, str(Path(__file__).parent / "backend"))

os.environ["PATH"] = "/opt/homebrew/opt/openjdk@11/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home"

def extract_universe(unx_path):
    """Extract UNX file completely"""
    print(f"\n{'='*80}")
    print(f"EXTRACTING: {unx_path.name}")
    print(f"{'='*80}")

    # Step 1: Extract outer UNX
    extract_dir = Path("/tmp/universe_test")
    extract_dir.mkdir(exist_ok=True)

    print(f"\nStep 1: Extracting outer UNX file...")
    with zipfile.ZipFile(unx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    files = list(extract_dir.glob("*"))
    print(f"✓ Extracted {len(files)} files:")
    for f in files:
        if f.is_file():
            size = f.stat().st_size
            print(f"  - {f.name} ({size:,} bytes)")

    # Step 2: Find and extract .blx file (business layer)
    blx_files = list(extract_dir.glob("*.blx"))
    if blx_files:
        blx_outer = blx_files[0]
        print(f"\nStep 2: Extracting inner BLX file: {blx_outer.name}")

        blx_dir = extract_dir / "blx_extracted"
        blx_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(blx_outer, 'r') as zip_ref:
            zip_ref.extractall(blx_dir)

        blx_files_inner = list(blx_dir.glob("*.blx"))
        print(f"✓ Found {len(blx_files_inner)} .blx files inside:")
        for f in blx_files_inner:
            size = f.stat().st_size
            print(f"  - {f.name} ({size:,} bytes)")

            # Check if this is a ZIP or binary
            try:
                with zipfile.ZipFile(f, 'r'):
                    print(f"    → This is ANOTHER ZIP file")
            except:
                print(f"    → This is BINARY/ENCRYPTED data")

                # Read first few bytes
                with open(f, 'rb') as binary:
                    header = binary.read(100)
                    print(f"    → First 20 bytes (hex): {header[:20].hex()}")

                return f  # Return the final binary file

    # Step 3: Same for .dfx
    dfx_files = list(extract_dir.glob("*.dfx"))
    if dfx_files:
        dfx_outer = dfx_files[0]
        print(f"\nStep 3: Extracting inner DFX file: {dfx_outer.name}")

        dfx_dir = extract_dir / "dfx_extracted"
        dfx_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(dfx_outer, 'r') as zip_ref:
            zip_ref.extractall(dfx_dir)

        dfx_files_inner = list(dfx_dir.glob("*.dfx"))
        print(f"✓ Found {len(dfx_files_inner)} .dfx files inside:")
        for f in dfx_files_inner:
            size = f.stat().st_size
            print(f"  - {f.name} ({size:,} bytes)")

            try:
                with zipfile.ZipFile(f, 'r'):
                    print(f"    → This is ANOTHER ZIP file")
            except:
                print(f"    → This is BINARY/ENCRYPTED data")

    return blx_files_inner[0] if blx_files_inner else None


def test_sdk_loading(binary_file):
    """Test loading the binary file with SDK"""
    print(f"\n{'='*80}")
    print(f"TESTING SDK LOADING")
    print(f"{'='*80}")

    import jpype
    import jpype.imports

    # Build SDK classpath
    sdk_dir = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"
    jar_files = list(sdk_dir.glob("**/*.jar"))

    print(f"\nStarting JVM with {len(jar_files)} SDK JARs...")
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        f"-Djava.class.path={':'.join(str(j) for j in jar_files)}",
        "-Xmx2048m"
    )
    print("✓ JVM started")

    # Try different SDK approaches
    print(f"\n--- Approach 1: EMF ResourceSet ---")
    try:
        from org.eclipse.emf.common.util import URI
        from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl

        resource_set = ResourceSetImpl()
        uri = URI.createFileURI(str(binary_file.absolute()))
        print(f"Loading: {uri}")

        resource = resource_set.getResource(uri, True)
        print(f"Resource: {resource}")

        if resource and resource.getContents():
            print(f"✓ SUCCESS! Contents count: {resource.getContents().size()}")
            universe = resource.getContents().get(0)
            print(f"Universe object: {universe}")
            print(f"Universe type: {type(universe)}")

            # Try to get metadata
            print(f"\nTrying to access universe properties:")
            try:
                print(f"  - Methods: {[m for m in dir(universe) if not m.startswith('_')][:20]}")
            except:
                pass

            return True
        else:
            print("✗ No contents in resource")
    except Exception as e:
        print(f"✗ Failed: {e}")

    print(f"\n--- Approach 2: UniverseFactory ---")
    try:
        from com.businessobjects.mds.universe import UniverseFactory

        factory = UniverseFactory.eINSTANCE
        print(f"Factory: {factory}")

        # Try to create/load universe
        universe = factory.createUniverse()
        print(f"Created universe: {universe}")

    except Exception as e:
        print(f"✗ Failed: {e}")

    print(f"\n--- Approach 3: Direct File Reading ---")
    try:
        # Check if there's a file input stream approach
        from java.io import FileInputStream
        from java.io import File

        java_file = File(str(binary_file.absolute()))
        print(f"Java File: {java_file}")
        print(f"  Exists: {java_file.exists()}")
        print(f"  Size: {java_file.length()}")
        print(f"  Can Read: {java_file.canRead()}")

        fis = FileInputStream(java_file)
        print(f"✓ Opened file stream")

        # Read first few bytes
        buffer = jpype.JArray(jpype.JByte)(100)
        count = fis.read(buffer)
        print(f"Read {count} bytes")

        # Check if it's a known format
        header_bytes = bytes([b & 0xff for b in buffer[:20]])
        print(f"Header hex: {header_bytes.hex()}")
        print(f"Header text: {header_bytes}")

        fis.close()

    except Exception as e:
        print(f"✗ Failed: {e}")

    jpype.shutdownJVM()
    return False


if __name__ == "__main__":
    print("="*80)
    print("FILE EXTRACTION VERIFICATION TEST")
    print("="*80)

    # Test with Oracle universe
    unx_file = Path("/Users/I870089/pipeline/input/Version 2 - for SAP BI 4.x/BOEXI40-Audit-Oracle.unx")

    if not unx_file.exists():
        print(f"✗ File not found: {unx_file}")
        sys.exit(1)

    # Extract completely
    binary_file = extract_universe(unx_file)

    if binary_file:
        print(f"\n{'='*80}")
        print(f"EXTRACTION SUCCESSFUL")
        print(f"{'='*80}")
        print(f"Final binary file: {binary_file}")
        print(f"Size: {binary_file.stat().st_size:,} bytes")

        # Test SDK loading
        success = test_sdk_loading(binary_file)

        if success:
            print(f"\n{'='*80}")
            print(f"✅ SUCCESS - File extracted AND loaded by SDK")
            print(f"{'='*80}")
        else:
            print(f"\n{'='*80}")
            print(f"⚠️  PARTIAL SUCCESS - File extracted but SDK needs correct API")
            print(f"{'='*80}")
    else:
        print(f"\n✗ Extraction failed")
