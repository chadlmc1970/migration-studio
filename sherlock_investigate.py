#!/usr/bin/env python3
"""
Sherlock Holmes Investigation: Find the Binary Deserializer
Follow the clues in the SDK JARs to crack the case!
"""
import sys
import os
from pathlib import Path
import zipfile
import re

sys.path.insert(0, str(Path(__file__).parent / "backend"))

os.environ["PATH"] = "/opt/homebrew/opt/openjdk@11/bin:" + os.environ.get("PATH", "")
os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home"

def print_clue(number, description):
    """Print a numbered clue"""
    print(f"\n🔍 CLUE #{number}: {description}")
    print("=" * 80)

def search_jar_for_classes(jar_path, patterns):
    """Search a JAR file for class names matching patterns"""
    matches = []
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            for name in jar.namelist():
                if name.endswith('.class'):
                    class_name = name.replace('/', '.').replace('.class', '')
                    for pattern in patterns:
                        if re.search(pattern, class_name, re.IGNORECASE):
                            matches.append((jar_path.name, class_name))
    except:
        pass
    return matches

def investigate():
    """Run the investigation"""
    print("=" * 80)
    print("🕵️  SHERLOCK HOLMES INVESTIGATION")
    print("   The Case of the Encrypted Binary Files")
    print("=" * 80)

    sdk_dir = Path(__file__).parent / "backend/app/engines/bobj2sac/sdk/BOBJ_SDK"
    jar_files = list(sdk_dir.glob("**/*.jar"))

    print(f"\n📚 Evidence Locker: {len(jar_files)} JAR files to investigate")

    # CLUE 1: Look for binary-related classes
    print_clue(1, "Search for 'Binary' resource classes")
    patterns = [
        r'binary.*resource',
        r'resource.*binary',
        r'binaryresource',
        r'.*BinaryResource.*'
    ]

    matches = []
    for jar in jar_files[:100]:  # Sample first 100
        matches.extend(search_jar_for_classes(jar, patterns))

    if matches:
        print(f"Found {len(matches)} suspects:")
        for jar, cls in matches[:20]:
            print(f"  📄 {jar} → {cls}")
    else:
        print("  No direct 'BinaryResource' classes found")

    # CLUE 2: Look for .blx/.dfx/.cnx handlers
    print_clue(2, "Search for .blx/.dfx/.cnx extension handlers")
    patterns = [
        r'\.blx',
        r'\.dfx',
        r'\.cnx',
        r'BusinessLayer',
        r'DataFoundation',
        r'Connection'
    ]

    matches = []
    for jar in jar_files[:100]:
        matches.extend(search_jar_for_classes(jar, patterns))

    if matches:
        print(f"Found {len(matches)} suspects:")
        for jar, cls in set(matches[:20]):
            print(f"  📄 {jar} → {cls}")

    # CLUE 3: Look for serialization/deserialization
    print_clue(3, "Search for serialization classes")
    patterns = [
        r'serializ',
        r'deserializ',
        r'.*Serializer',
        r'.*Deserializer'
    ]

    matches = []
    for jar in jar_files[:100]:
        matches.extend(search_jar_for_classes(jar, patterns))

    if matches:
        print(f"Found {len(matches)} suspects:")
        for jar, cls in set(matches[:20]):
            print(f"  📄 {jar} → {cls}")

    # CLUE 4: Search actual JAR contents for .blx/.dfx/.cnx references
    print_clue(4, "Search JAR contents for extension references")

    suspicious_jars = []
    for jar in jar_files:
        if any(keyword in jar.name.lower() for keyword in ['universe', 'mds', 'semantic', 'business']):
            suspicious_jars.append(jar)

    print(f"Found {len(suspicious_jars)} suspicious JARs with universe-related names:")
    for jar in suspicious_jars[:20]:
        print(f"  📦 {jar.name}")

    # CLUE 5: Start JVM and interrogate the SDK directly
    print_clue(5, "Interrogate the SDK classes directly with JVM")

    import jpype
    import jpype.imports

    print("Starting JVM...")
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        f"-Djava.class.path={':'.join(str(j) for j in jar_files)}",
        "-Xmx2048m"
    )

    print("✓ JVM started\n")

    # Check ResourceSet registry for registered factories
    from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
    from org.eclipse.emf.ecore.resource import Resource

    resource_set = ResourceSetImpl()
    registry = resource_set.getResourceFactoryRegistry()

    print("🔍 Checking Resource Factory Registry:")

    # Check extension map
    ext_map = registry.getExtensionToFactoryMap()
    print(f"\n  Registered extensions: {ext_map.size()}")
    for key in ext_map.keySet():
        factory = ext_map.get(key)
        print(f"    • .{key} → {factory.getClass().getName()}")

    # Check protocol map
    protocol_map = registry.getProtocolToFactoryMap()
    print(f"\n  Registered protocols: {protocol_map.size()}")
    for key in protocol_map.keySet():
        factory = protocol_map.get(key)
        print(f"    • {key} → {factory.getClass().getName()}")

    # Check content type map
    content_map = registry.getContentTypeToFactoryMap()
    print(f"\n  Registered content types: {content_map.size()}")
    for key in content_map.keySet():
        factory = content_map.get(key)
        print(f"    • {key} → {factory.getClass().getName()}")

    # CLUE 6: Try to find ResourceFactory implementations
    print_clue(6, "Search for ResourceFactory implementations in loaded classes")

    try:
        # Look for all loaded Resource.Factory implementations
        from java.lang import ClassLoader, Class

        # Check specific SAP packages
        print("\nTrying to import SAP-specific classes:")

        sap_packages = [
            "com.businessobjects.mds.universe.impl",
            "com.businessobjects.mds.universe.util",
            "com.businessobjects.mds.universe.io",
            "com.businessobjects.mds.universe.resource",
            "com.businessobjects.mds",
            "com.sap.sl.sdk.authoring"
        ]

        for package in sap_packages:
            print(f"\n  Package: {package}")
            try:
                # Try common class names
                possible_classes = [
                    f"{package}.UniverseResourceFactory",
                    f"{package}.UniverseResourceFactoryImpl",
                    f"{package}.ResourceFactory",
                    f"{package}.BinaryResourceFactory",
                    f"{package}.UniverseResource",
                    f"{package}.UniverseLoader",
                    f"{package}.UniverseReader"
                ]

                for cls_name in possible_classes:
                    try:
                        cls = jpype.JClass(cls_name)
                        print(f"    ✓ FOUND: {cls_name}")

                        # Try to get methods
                        methods = [m for m in dir(cls) if not m.startswith('_')]
                        print(f"      Methods: {methods[:10]}")
                    except:
                        pass
            except:
                pass

    except Exception as e:
        print(f"  Investigation note: {e}")

    # CLUE 7: Check UniversePackage for resource factory registration
    print_clue(7, "Check UniversePackage for factory registration")

    try:
        from com.businessobjects.mds.universe import UniversePackage

        package = UniversePackage.eINSTANCE
        print(f"UniversePackage: {package}")
        print(f"NS URI: {package.getNsURI()}")
        print(f"NS Prefix: {package.getNsPrefix()}")

        # Check if there's a resource factory descriptor
        print(f"\nPackage methods:")
        methods = [m for m in dir(package) if 'resource' in m.lower() or 'factory' in m.lower()]
        for m in methods:
            print(f"  • {m}")

    except Exception as e:
        print(f"Could not access UniversePackage: {e}")

    # CLUE 8: The binary header clue
    print_clue(8, "Analyze the binary header signature")

    print("Binary header: 04 00 00 00 00 1a 02 01 00 10 00 00 c3 e0 3d 6d 5d 2f 36 5a")
    print("\nDeduction:")
    print("  • Byte 0-3: 04 00 00 00 → Version marker (little-endian int = 4)?")
    print("  • Byte 4-7: 00 1a 02 01 → Format identifier?")
    print("  • Remaining: Likely compressed or encrypted data")
    print("\n  Hypothesis: This is NOT standard EMF XMI format")
    print("  Hypothesis: This IS a proprietary SAP serialization format")
    print("  Hypothesis: SDK must have custom ResourceFactory for this format")

    jpype.shutdownJVM()

    # THE CONCLUSION
    print("\n" + "=" * 80)
    print("🎯 SHERLOCK'S CONCLUSION")
    print("=" * 80)
    print("""
Based on the evidence:

1. Files are NOT standard EMF XMI (which would start with <?xml or have XML headers)
2. Binary header '04000000' suggests proprietary SAP format version 4
3. SDK contains universe classes but ResourceFactory registry is EMPTY by default
4. EMF requires manual registration of resource factories for custom formats

THEORY: SAP SDK requires:
  a) Finding the specific UniverseResourceFactory class
  b) Manually registering it for .blx/.dfx/.cnx extensions
  c) OR using a different loading mechanism entirely (not EMF ResourceSet)

NEXT STEPS:
  → Search SDK JARs more thoroughly for UniverseResourceFactory
  → Try Universe-specific loading APIs (not generic EMF)
  → Check if SDK has documentation files in the JARs
  → Try CMS (Central Management Server) connection approach
""")

if __name__ == "__main__":
    investigate()
