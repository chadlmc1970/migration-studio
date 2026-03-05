"""Pipeline Runner - Orchestrates the transformation process"""
from pathlib import Path
from .loaders import load_cim, scan_cim_directory, generate_mock_cim
from .graph import SemanticGraph
from .generators import generate_sac_model, generate_datasphere_views, generate_hana_schema
from .logging import TransformReport
from .state_manager import PipelineState, EventLogger
from app.config import AI_ENABLED
from .ai.semantic_enhancer import SemanticEnhancer


class PipelineRunner:
    """Orchestrate CIM transformation pipeline"""

    def __init__(self, pipeline_root: Path = Path("/pipeline")):
        self.pipeline_root = pipeline_root
        self.cim_dir = pipeline_root / "cim"
        self.targets_dir = pipeline_root / "targets"
        self.logs_dir = pipeline_root / "logs" / "transform"
        self.state_file = pipeline_root / "state" / "pipeline_state.json"
        self.events_file = pipeline_root / "events" / "events.log"

        self.state_manager = PipelineState(self.state_file)
        self.event_logger = EventLogger(self.events_file)

    def run(self, force: bool = False) -> list[dict]:
        """Run the transformation pipeline"""
        print(f"🔍 Scanning CIM directory: {self.cim_dir}")
        print(f"📊 Loading pipeline state: {self.state_file}")

        cim_files = scan_cim_directory(self.cim_dir)

        if not cim_files:
            print("⚠️  No CIM files found. Generating mock CIM...")
            mock_path = self.cim_dir / "sales_universe.cim.json"
            generate_mock_cim(mock_path)
            cim_files = [mock_path]
            print(f"✓ Generated mock CIM: {mock_path}")

            # Initialize state for mock universe
            universe_id = "sales_universe"
            universes = self.state_manager.state.get("universes", {})
            if universe_id not in universes:
                if "universes" not in self.state_manager.state:
                    self.state_manager.state["universes"] = {}
                self.state_manager.state["universes"][universe_id] = {
                    "parsed": True,
                    "transformed": False,
                    "validated": False
                }
                self.state_manager.save_state()

        results = []
        processed_count = 0
        skipped_count = 0

        for cim_file in cim_files:
            # Extract universe ID from filename
            universe_id = cim_file.stem.replace('.cim', '')

            # Check if transformation is needed
            if not force and not self.state_manager.needs_transformation(universe_id):
                print(f"\n⏭️  Skipping {universe_id}: already transformed or not parsed")
                skipped_count += 1
                continue

            print(f"\n{'='*60}")
            print(f"Processing: {cim_file.name}")
            print(f"{'='*60}")

            result = self._process_cim(cim_file)
            results.append(result)
            processed_count += 1

        print(f"\n{'='*60}")
        print(f"✅ Transformation complete!")
        print(f"   Processed: {processed_count} universe(s)")
        print(f"   Skipped: {skipped_count} universe(s)")
        print(f"{'='*60}\n")

        return results

    def _process_cim(self, cim_file: Path) -> dict:
        """Process a single CIM file"""

        # Load CIM
        print("📥 Loading CIM...")
        cim = load_cim(cim_file)
        print(f"✓ Loaded universe: {cim.universe.name} (id: {cim.universe.id})")

        # === AI SEMANTIC ENHANCEMENT ===
        if AI_ENABLED:
            try:
                print("🧠 Running AI semantic enhancement...")
                enhancer = SemanticEnhancer()

                # Convert CIM to dict for enhancement
                cim_dict = cim.model_dump() if hasattr(cim, 'model_dump') else cim.dict()
                enhanced_dict = enhancer.enhance_cim(cim_dict)

                # Extract enhancement results
                if enhanced_dict.get("ai_enhancements"):
                    ai = enhanced_dict["ai_enhancements"]
                    hierarchies = len(ai.get("detected_hierarchies", []))
                    formulas = len(ai.get("translated_formulas", {}))
                    classifications = len(ai.get("dimension_classifications", {}))

                    print(f"✓ AI enhancement complete:")
                    print(f"   - {classifications} dimension(s) classified")
                    print(f"   - {hierarchies} hierarchy(ies) detected")
                    print(f"   - {formulas} formula(s) translated")

                    # Store enhancements back in CIM
                    if not hasattr(cim, 'ai_enhancements'):
                        cim.ai_enhancements = ai

            except Exception as e:
                print(f"⚠️  AI enhancement failed (non-critical): {e}")
                print("   Continuing with basic transformation...")
        else:
            print("ℹ️  AI enhancement disabled")
        # === END AI ENHANCEMENT ===

        # Log transformation start
        self.event_logger.log_event("transform_started", cim.universe.id)

        try:
            # Create output directories
            universe_dir = self.targets_dir / cim.universe.id
            sac_dir = universe_dir / "sac"
            datasphere_dir = universe_dir / "datasphere"
            hana_dir = universe_dir / "hana"

            # Build semantic graph
            print("🔗 Building semantic graph...")
            graph = SemanticGraph(cim)
            print(f"✓ Graph built: {len(graph.get_all_tables())} tables, connected: {graph.is_connected()}")

            # Generate SAC model
            print("🎯 Generating SAC model...")
            sac_model = generate_sac_model(cim, sac_dir)
            print(f"✓ SAC model generated: {sac_dir / 'model.json'}")

            # Generate Datasphere views
            print("💾 Generating Datasphere views...")
            datasphere_sql = generate_datasphere_views(cim, datasphere_dir)
            print(f"✓ Datasphere views generated: {datasphere_dir / 'views.sql'}")

            # Generate HANA schema
            print("🗄️  Generating HANA schema...")
            hana_sql = generate_hana_schema(cim, hana_dir)
            print(f"✓ HANA schema generated: {hana_dir / 'schema.sql'}")

            # Generate transformation report
            print("📊 Generating transformation report...")
            report = TransformReport(cim)
            report_path = self.logs_dir / f"{cim.universe.id}_transform_report.json"
            report_data = report.generate_report(report_path)
            print(f"✓ Report generated: {report_path}")

            if report_data["warnings"]:
                print(f"⚠️  {len(report_data['warnings'])} warning(s):")
                for warning in report_data["warnings"]:
                    print(f"   - {warning}")

            # Update pipeline state
            print("📝 Updating pipeline state...")
            self.state_manager.mark_transformed(cim.universe.id)
            print(f"✓ State updated: transformed = true")

            # Log successful transformation
            self.event_logger.log_event("transform_completed", cim.universe.id)

            print(f"\n✅ Transformation complete for {cim.universe.id}")

            return {
                "universe_id": cim.universe.id,
                "cim_file": str(cim_file),
                "output_dir": str(universe_dir),
                "report": report_data,
                "status": "success"
            }

        except Exception as e:
            # Log transformation failure
            self.event_logger.log_event("transform_failed", cim.universe.id, str(e))
            print(f"\n❌ Transformation failed for {cim.universe.id}: {e}")

            return {
                "universe_id": cim.universe.id,
                "cim_file": str(cim_file),
                "status": "failed",
                "error": str(e)
            }
