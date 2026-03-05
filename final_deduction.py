#!/usr/bin/env python3
"""
The Final Deduction: Register a Custom ResourceFactory for .blx/.dfx/.cnx
Based on EMF patterns, we need to create and register our own ResourceFactory
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

os.environ["PATH"] = "/opt/homebrew/opt/openjdk@11/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home"

import jpype
import jpype.imports

def final_attempt():
    """Try registering a custom resource factory"""

    print("=" * 80)
    print("🎯 THE FINAL DEDUCTION")
    print("=" * 80)

    sdk_dir = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"
    jar_files = list(sdk_dir.glob("**/*.jar"))

    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        f"-Djava.class.path={':'.join(str(j) for j in jar_files)}",
        "-Xmx2048m"
    )

    print("\n📋 HYPOTHESIS:")
    print("The binary .blx/.dfx/.cnx files use EMF binary serialization")
    print("EMF has a BinaryResourceImpl class for binary formats")
    print()

    binary_file = Path("/tmp/universe_test/blx_extracted/BOEXI40-Audit-Oracle.blx")

    # Try 1: EMF Binary Resource
    print("=" * 80)
    print("ATTEMPT 1: EMF Binary Resource")
    print("=" * 80)

    try:
        from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl, BinaryResourceImpl
        from org.eclipse.emf.common.util import URI
        from com.businessobjects.mds.universe import UniversePackage

        # Register package
        package = UniversePackage.eINSTANCE
        from org.eclipse.emf.ecore import EPackage
        registry = EPackage.Registry.INSTANCE
        registry.put(package.getNsURI(), package)
        print(f"✓ Registered UniversePackage")

        # Create binary resource directly
        resource_set = ResourceSetImpl()
        uri = URI.createFileURI(str(binary_file.absolute()))

        print(f"\nCreating BinaryResourceImpl directly...")
        resource = BinaryResourceImpl(uri)
        print(f"✓ Created: {resource}")

        # Try to load
        print(f"Loading...")
        resource.load(None)

        if resource.getContents() and resource.getContents().size() > 0:
            print(f"\n✅✅✅ SUCCESS! Loaded {resource.getContents().size()} objects!")

            obj = resource.getContents().get(0)
            print(f"\nObject: {obj}")
            print(f"Type: {type(obj)}")

            return True

    except ImportError as e:
        print(f"✗ BinaryResourceImpl not available: {e}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()

    # Try 2: Search for all Resource.Factory implementations
    print("\n" + "=" * 80)
    print("ATTEMPT 2: Find ALL ResourceFactory implementations")
    print("=" * 80)

    try:
        from org.eclipse.emf.ecore.resource import Resource
        print(f"Resource.Factory interface: {Resource.Factory}")

        # Try to find implementations by searching loaded classes
        print("\nSearching for ResourceFactory implementations in SDK...")

        # Check common EMF resource factory packages
        packages_to_check = [
            "org.eclipse.emf.ecore.resource.impl",
            "org.eclipse.emf.ecore.xmi.impl",
            "com.businessobjects.mds.universe.resource",
            "com.businessobjects.mds.resource",
            "com.businessobjects.mds.impl",
        ]

        for pkg in packages_to_check:
            print(f"\n  Checking package: {pkg}")
            factory_classes = [
                f"{pkg}.ResourceFactoryImpl",
                f"{pkg}.UniverseResourceFactory",
                f"{pkg}.UniverseResourceFactoryImpl",
                f"{pkg}.BinaryResourceFactory",
                f"{pkg}.BinaryResourceFactoryImpl",
            ]

            for cls_name in factory_classes:
                try:
                    cls = jpype.JClass(cls_name)
                    print(f"    ✓✓✓ FOUND: {cls_name}")

                    # Try to instantiate and use it
                    try:
                        factory = cls()
                        print(f"        Instantiated: {factory}")

                        # Register it
                        from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
                        from org.eclipse.emf.common.util import URI
                        from com.businessobjects.mds.universe import UniversePackage

                        resource_set = ResourceSetImpl()
                        registry = resource_set.getResourceFactoryRegistry()

                        # Register for .blx extension
                        ext_map = registry.getExtensionToFactoryMap()
                        ext_map.put("blx", factory)
                        ext_map.put("dfx", factory)
                        ext_map.put("cnx", factory)
                        print(f"        ✓ Registered for .blx/.dfx/.cnx")

                        # Try loading
                        uri = URI.createFileURI(str(binary_file.absolute()))
                        print(f"        Loading {uri}...")

                        resource = resource_set.getResource(uri, True)

                        if resource and resource.getContents() and resource.getContents().size() > 0:
                            print(f"\n        ✅✅✅ SUCCESS! Loaded {resource.getContents().size()} objects!")
                            obj = resource.getContents().get(0)
                            print(f"        Object: {obj}")
                            return True

                    except Exception as e:
                        print(f"        Failed to use: {e}")

                except:
                    pass

    except Exception as e:
        print(f"✗ Search failed: {e}")

    # Try 3: Use XMI with binary data handler
    print("\n" + "=" * 80)
    print("ATTEMPT 3: Try Ecore Util to load")
    print("=" * 80)

    try:
        from org.eclipse.emf.ecore.util import EcoreUtil
        from org.eclipse.emf.common.util import URI
        from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
        from com.businessobjects.mds.universe import UniversePackage

        # Register package
        package = UniversePackage.eINSTANCE
        from org.eclipse.emf.ecore import EPackage
        registry = EPackage.Registry.INSTANCE
        registry.put(package.getNsURI(), package)

        # Create resource set
        resource_set = ResourceSetImpl()

        # Create resource with factory registration attempt
        from org.eclipse.emf.ecore.xmi.impl import XMIResourceFactoryImpl
        factory_registry = resource_set.getResourceFactoryRegistry()

        # Try wildcard registration
        factory_registry.getExtensionToFactoryMap().put("*", XMIResourceFactoryImpl())
        print("✓ Registered XMI factory for all extensions")

        uri = URI.createFileURI(str(binary_file.absolute()))
        print(f"Loading: {uri}")

        resource = resource_set.getResource(uri, True)

        if resource and resource.getContents() and resource.getContents().size() > 0:
            print(f"\n✅✅✅ SUCCESS! Loaded {resource.getContents().size()} objects!")
            return True

    except Exception as e:
        print(f"✗ Failed: {e}")

    jpype.shutdownJVM()

    print("\n" + "=" * 80)
    print("🔍 FINAL CONCLUSION")
    print("=" * 80)
    print("""
ALL ATTEMPTS FAILED.

The binary .blx/.dfx/.cnx files are using a proprietary SAP format that is:
1. NOT standard EMF XMI (XML)
2. NOT standard EMF binary serialization
3. REQUIRES a custom ResourceFactory that doesn't exist in the SDK

POSSIBILITIES:
1. Files are encrypted and need decryption key/license
2. Files require CMS server connection to decrypt
3. SDK is incomplete (missing ResourceFactory implementation)
4. We need different SAP SDK (Semantic Layer SDK instead of MDS SDK)

RECOMMENDATION:
Deploy current system with placeholder mode and document that full
metadata extraction requires SAP server connection or additional SDK components.
""")

    return False

if __name__ == "__main__":
    success = final_attempt()
    sys.exit(0 if success else 1)
