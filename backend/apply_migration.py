"""
Apply database migrations to Neon PostgreSQL
Run this after deploying code changes that modify the database schema
"""
import os
import psycopg2
from pathlib import Path

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    exit(1)

# Migration file
migration_file = Path(__file__).parent / "migrations" / "002_add_artifact_content.sql"

if not migration_file.exists():
    print(f"❌ Migration file not found: {migration_file}")
    exit(1)

print("=====================================")
print("Database Migration")
print("=====================================")
print(f"Target: {DATABASE_URL.split('@')[1]}")  # Hide password
print(f"Migration: {migration_file.name}")
print("")

# Read migration SQL
with open(migration_file) as f:
    migration_sql = f.read()

print("Migration SQL:")
print("-" * 40)
print(migration_sql[:500] + "..." if len(migration_sql) > 500 else migration_sql)
print("-" * 40)
print("")

# Confirm
response = input("Apply this migration to production? (yes/no): ")
if response.lower() != "yes":
    print("❌ Migration cancelled")
    exit(0)

# Connect and apply migration
try:
    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print("Applying migration...")
    cursor.execute(migration_sql)
    conn.commit()

    print("✅ Migration applied successfully!")

    # Verify changes
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'artifacts'
        ORDER BY ordinal_position
    """)

    print("")
    print("Artifacts table columns:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Migration failed: {e}")
    exit(1)

print("")
print("=====================================")
print("✅ Migration Complete")
print("=====================================")
print("")
print("Next: Trigger pipeline run to populate artifacts")
print("  curl -X POST https://migration-studio-api.onrender.com/api/run-pipeline")
