#!/bin/bash
# Setup SAP BusinessObjects SDK Integration
# Run this after copying BOBJ_SDK folder from Windows

set -e

echo "======================================"
echo "SAP BOBJ SDK Setup"
echo "======================================"
echo ""

# 1. Check if SDK folder exists
SDK_DIR="backend/app/engines/bobj2sac/sdk/BOBJ_SDK"

if [ ! -d "$SDK_DIR" ]; then
    echo "❌ SDK folder not found at: $SDK_DIR"
    echo ""
    echo "Please copy BOBJ_SDK folder from Windows:"
    echo "  1. In Windows: Desktop\\BOBJ_SDK"
    echo "  2. Drag to Mac Desktop"
    echo "  3. Move to: $(pwd)/$SDK_DIR"
    echo ""
    exit 1
fi

# Count JAR files
JAR_COUNT=$(find "$SDK_DIR" -name "*.jar" | wc -l)
echo "✓ Found $JAR_COUNT JAR files in SDK"

if [ "$JAR_COUNT" -eq 0 ]; then
    echo "❌ No JAR files found in SDK directory"
    exit 1
fi

echo ""

# 2. Install Java
echo "[1/3] Installing Java OpenJDK 11..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1)
    echo "✓ Java already installed: $JAVA_VERSION"
else
    echo "Installing OpenJDK 11 via Homebrew..."
    brew install openjdk@11

    # Add to PATH
    echo 'export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"' >> ~/.zshrc
    export PATH="/opt/homebrew/opt/openjdk@11/bin:$PATH"

    echo "✓ Java installed"
fi

echo ""

# 3. Install JPype
echo "[2/3] Installing JPype (Python-Java bridge)..."
pip install JPype1

echo "✓ JPype installed"
echo ""

# 4. Test SDK integration
echo "[3/3] Testing SDK integration..."

python3 << 'PYTHON'
import sys
sys.path.insert(0, 'backend/app/engines')

try:
    from bobj2sac.sdk_bridge import BOBJSDKBridge, SDKInfo

    print("  - Starting JVM with SDK...")
    if BOBJSDKBridge.start_jvm():
        print("  ✓ JVM started successfully")

        # Get SDK version
        version = SDKInfo.get_sdk_version()
        if version:
            print(f"  ✓ SAP BOBJ SDK version: {version}")

        # List available classes
        print("  - Discovering SDK classes...")
        SDKInfo.list_available_classes()

        BOBJSDKBridge.shutdown_jvm()
        print("  ✓ SDK integration test passed!")

    else:
        print("  ❌ Failed to start JVM")
        sys.exit(1)

except Exception as e:
    print(f"  ❌ SDK test failed: {e}")
    sys.exit(1)
PYTHON

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ SDK Setup Complete!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "  1. Test UNV parsing: python -m bobj2sac.io.unv <file.unv>"
    echo "  2. Complete SDK parser implementation"
    echo "  3. Deploy to production"
    echo ""
else
    echo ""
    echo "❌ Setup failed - check errors above"
    exit 1
fi
