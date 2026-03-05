#!/usr/bin/env python3
"""
Sherlock Holmes: Deep Dive Investigation
Following the UniversePackage lead - eDirectResource() looks suspicious!
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

os.environ["PATH"] = "/opt/homebrew/opt/openjdk@11/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home"

import jpype
import jpype.imports

def investigate_universe_package():
    """Deep dive into UniversePackage resource methods"""

    print("=" * 80)
    print("🔍 DEEP DIVE: UniversePackage Resource Methods")
    print("=" * 80)

    sdk_dir = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"
    jar_files = list(sdk_dir.glob("**/*.jar"))

    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        f"-Djava.class.path={':'.join(str(j) for j in jar_files)}",
        "-Xmx2048m"
    )

    from com.businessobjects.mds.universe import UniversePackage, UniverseFactory
    from org.eclipse.emf.common.util import URI
    from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl

    package = UniversePackage.eINSTANCE
    factory = UniverseFactory.eINSTANCE

    print("\n📋 CLUE: UniversePackage has 'eDirectResource' method!")
    print("=" * 80)

    # Try to use the direct resource method
    binary_file = Path("/tmp/universe_test/blx_extracted/BOEXI40-Audit-Oracle.blx")

    print(f"\n1. Testing eDirectResource() approach:")
    print(f"   File: {binary_file}")

    try:
        uri = URI.createFileURI(str(binary_file.absolute()))
        print(f"   URI: {uri}")

        # Create resource set
        resource_set = ResourceSetImpl()

        # Try getting package resource
        print(f"\n   Calling package.eDirectResource()...")
        direct_resource = package.eDirectResource()
        print(f"   Result: {direct_resource}")

        if direct_resource:
            print(f"   Type: {type(direct_resource)}")
            print(f"   URI: {direct_resource.getURI()}")

    except Exception as e:
        print(f"   ⚠ Note: {e}")

    # CLUE: Try factory methods
    print(f"\n2. Testing UniverseFactory methods:")
    print("=" * 80)

    print("\n   All factory methods:")
    factory_methods = [m for m in dir(factory) if not m.startswith('_')]
    for m in sorted(factory_methods):
        print(f"     • {m}")

    # Look for create methods
    print(f"\n   Create methods:")
    create_methods = [m for m in factory_methods if 'create' in m.lower()]
    for m in create_methods:
        print(f"     ✓ {m}")
        try:
            method = getattr(factory, m)
            # Try to get signature if possible
            print(f"       {method}")
        except:
            pass

    # CLUE: Try to load using UniverseFactory with file parameter
    print(f"\n3. Testing if UniverseFactory can load from file:")
    print("=" * 80)

    # Check if there's a load/open/read method
    load_methods = [m for m in dir(factory) if any(k in m.lower() for k in ['load', 'open', 'read', 'import'])]

    if load_methods:
        print(f"   Found potential loading methods:")
        for m in load_methods:
            print(f"     ✓ {m}")
    else:
        print(f"   No direct load methods found on UniverseFactory")

    # CLUE: Check Universe object for setters
    print(f"\n4. Testing Universe object methods:")
    print("=" * 80)

    universe = factory.createUniverse()
    print(f"   Created empty universe: {universe}")

    # Look for methods that might load data
    universe_methods = [m for m in dir(universe) if not m.startswith('_')]

    load_methods = [m for m in universe_methods if any(k in m.lower() for k in ['load', 'set', 'read', 'import', 'attach', 'bind'])]

    print(f"\n   Found {len(load_methods)} methods that might load data:")
    for m in sorted(load_methods)[:30]:
        print(f"     • {m}")

    # CLUE: Try ResourceSet with package registration
    print(f"\n5. Testing ResourceSet with UniversePackage registration:")
    print("=" * 80)

    try:
        from org.eclipse.emf.ecore import EPackage

        # Register the package
        print(f"   Registering UniversePackage...")
        ns_uri = package.getNsURI()
        print(f"   NS URI: {ns_uri}")

        # Get global package registry
        registry = EPackage.Registry.INSTANCE
        print(f"   Global registry: {registry}")

        # Register
        registry.put(ns_uri, package)
        print(f"   ✓ Package registered in global registry")

        # Now try to load
        resource_set = ResourceSetImpl()

        # Check if package is now available
        pkg = resource_set.getPackageRegistry().getEPackage(ns_uri)
        print(f"   Package in resource set: {pkg}")

        # Try loading the file
        print(f"\n   Attempting to load binary file with registered package...")
        uri = URI.createFileURI(str(binary_file.absolute()))

        resource = resource_set.getResource(uri, True)
        print(f"   Resource: {resource}")

        if resource and resource.getContents():
            contents = resource.getContents()
            print(f"   ✓✓✓ SUCCESS! Loaded {contents.size()} objects")

            if contents.size() > 0:
                obj = contents.get(0)
                print(f"\n   First object: {obj}")
                print(f"   Type: {type(obj)}")

                # Try to access properties
                if hasattr(obj, 'getBusinessName'):
                    print(f"   Business Name: {obj.getBusinessName()}")
        else:
            print(f"   ✗ Resource has no contents")

    except Exception as e:
        print(f"   ⚠ Error: {e}")
        import traceback
        traceback.print_exc()

    # CLUE: Check for CMS/Enterprise SDK approach
    print(f"\n6. Searching for CMS/Enterprise loading approach:")
    print("=" * 80)

    try:
        # Try to import CMS-related classes
        print(f"   Trying to import CMS classes...")

        from com.businessobjects.mds.repository.cms import CMSRepository
        print(f"   ✓ CMSRepository found: {CMSRepository}")

    except Exception as e:
        print(f"   Note: {e}")

    try:
        # Try SL SDK (Semantic Layer SDK)
        from com.sap.sl.sdk.authoring.businesslayer import BusinessLayer
        print(f"   ✓ BusinessLayer found: {BusinessLayer}")

        # Check methods
        bl_methods = [m for m in dir(BusinessLayer) if not m.startswith('_')]
        print(f"   Methods: {bl_methods[:20]}")

    except Exception as e:
        print(f"   Note: {e}")

    # CLUE: Search for DataFoundation class
    print(f"\n7. Searching for DataFoundation classes:")
    print("=" * 80)

    try:
        from com.businessobjects.mds.datafoundation import DataFoundation
        print(f"   ✓ DataFoundation found: {DataFoundation}")

        df_methods = [m for m in dir(DataFoundation) if not m.startswith('_')]
        print(f"   Methods: {df_methods[:20]}")

    except Exception as e:
        print(f"   Note: {e}")

    jpype.shutdownJVM()

    print("\n" + "=" * 80)
    print("🎯 INVESTIGATION SUMMARY")
    print("=" * 80)
    print("""
KEY FINDINGS:

1. UniversePackage has eDirectResource() method - but it's for package's own resource
2. UniverseFactory creates empty objects - no direct load methods found
3. ResourceSet requires ResourceFactory registration for binary formats
4. SDK has CMS/Repository classes - files might need CMS connection
5. SDK has DataFoundation/BusinessLayer classes - separate from Universe

BREAKTHROUGH HYPOTHESIS:
The binary .blx/.dfx/.cnx files are NOT standalone! They might require:
  → CMS connection to server
  → License/authentication
  → OR specific ResourceFactory implementation hidden in the SDK

NEXT STEPS:
  → Search for 'ResourceFactory' implementations in SDK JARs
  → Try to find documentation or sample code in JAR resources
  → Check if binary format is compressed/encrypted (might need decryption key)
""")

if __name__ == "__main__":
    investigate_universe_package()
