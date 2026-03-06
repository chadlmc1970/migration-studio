#!/bin/bash
# Build script for BLXParser Java wrapper

set -e

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
BIN_DIR="$SCRIPT_DIR/bin"

# Use SDK from project directory - need JARs from multiple locations
IDT_PLUGINS="/Users/I870089/migration_studio/backend/app/engines/bobj2sac/sdk/BOBJ_SDK/Information Design Tool/plugins"
TRANS_PLUGINS="/Users/I870089/migration_studio/backend/app/engines/bobj2sac/sdk/BOBJ_SDK/TransMgr/plugins"

if [ ! -d "$IDT_PLUGINS" ] || [ ! -d "$TRANS_PLUGINS" ]; then
    echo "Error: Could not find SAP BOBJ SDK plugins directories"
    exit 1
fi

echo "Found SDK plugins at: $IDT_PLUGINS and $TRANS_PLUGINS"

# Create bin directory
mkdir -p "$BIN_DIR"

# Build classpath
CLASSPATH="$BIN_DIR"
for jar in "$IDT_PLUGINS"/*.jar; do
    if [ -f "$jar" ]; then
        CLASSPATH="$CLASSPATH:$jar"
    fi
done
for jar in "$TRANS_PLUGINS"/*.jar; do
    if [ -f "$jar" ]; then
        CLASSPATH="$CLASSPATH:$jar"
    fi
done

echo "Building BLXParser..."
echo "Classpath: $CLASSPATH"

# Compile
javac -cp "$CLASSPATH" -d "$BIN_DIR" "$SRC_DIR/BLXParser.java"

if [ $? -eq 0 ]; then
    echo "Build successful! Compiled class to: $BIN_DIR"

    # Create run script
    cat > "$SCRIPT_DIR/run_parser.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"

# Use SDK from project directory
IDT_PLUGINS="/Users/I870089/migration_studio/backend/app/engines/bobj2sac/sdk/BOBJ_SDK/Information Design Tool/plugins"
TRANS_PLUGINS="/Users/I870089/migration_studio/backend/app/engines/bobj2sac/sdk/BOBJ_SDK/TransMgr/plugins"

if [ ! -d "$IDT_PLUGINS" ] || [ ! -d "$TRANS_PLUGINS" ]; then
    echo "Error: Could not find SAP BOBJ SDK plugins directories"
    exit 1
fi

# Build classpath
CLASSPATH="$BIN_DIR"
for jar in "$IDT_PLUGINS"/*.jar; do
    if [ -f "$jar" ]; then
        CLASSPATH="$CLASSPATH:$jar"
    fi
done
for jar in "$TRANS_PLUGINS"/*.jar; do
    if [ -f "$jar" ]; then
        CLASSPATH="$CLASSPATH:$jar"
    fi
done

# Run parser
java -cp "$CLASSPATH" BLXParser "$@"
EOF

    chmod +x "$SCRIPT_DIR/run_parser.sh"
    echo "Created run script: $SCRIPT_DIR/run_parser.sh"
else
    echo "Build failed!"
    exit 1
fi
