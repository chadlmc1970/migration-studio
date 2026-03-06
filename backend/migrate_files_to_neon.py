#!/usr/bin/env python3
"""
Migrate existing .unx files from filesystem to Neon database
Run this once on Render to populate source_unx artifacts
"""
import sys
from pathlib import Path
import base64

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.services.artifact_storage import ArtifactStorage
from app.models.database import Universe

PIPELINE_ROOT = Path.home() / "pipeline"
INPUT_DIR = PIPELINE_ROOT / "input"


def migrate_files():
    """Scan input directory and migrate .unx files to database"""
    db = SessionLocal()

    try:
        if not INPUT_DIR.exists():
            print(f"Input directory does not exist: {INPUT_DIR}")
            return

        unx_files = list(INPUT_DIR.glob("*.unx"))

        if not unx_files:
            print(f"No .unx files found in {INPUT_DIR}")
            return

        print(f"Found {len(unx_files)} .unx files")

        for unx_file in unx_files:
            universe_id = unx_file.stem  # Remove .unx extension

            print(f"\nProcessing: {unx_file.name}")

            # Read file content
            with open(unx_file, 'rb') as f:
                file_content = f.read()

            file_size = len(file_content)
            print(f"  Size: {file_size:,} bytes")

            # Check if universe exists
            universe = db.query(Universe).filter(Universe.id == universe_id).first()
            if not universe:
                print(f"  Creating universe record: {universe_id}")
                universe = Universe(
                    id=universe_id,
                    parsed=False,
                    transformed=False,
                    validated=False
                )
                db.add(universe)
                db.commit()

            # Save as artifact
            try:
                artifact = ArtifactStorage.save_binary_artifact(
                    db=db,
                    universe_id=universe_id,
                    artifact_type=ArtifactStorage.TYPE_SOURCE_UNX,
                    binary_content=file_content
                )
                print(f"  ✓ Saved artifact (id={artifact.id})")
            except Exception as e:
                print(f"  ✗ Failed to save artifact: {e}")

        print(f"\nMigration complete: {len(unx_files)} files processed")

    finally:
        db.close()


if __name__ == "__main__":
    migrate_files()
