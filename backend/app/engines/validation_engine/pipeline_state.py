"""
Pipeline State Manager - handles reading/writing pipeline state
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class PipelineStateManager:
    """Manages pipeline state file integration"""

    def __init__(self, pipeline_root: Path):
        self.pipeline_root = Path(pipeline_root)
        self.state_file = self.pipeline_root / "state" / "pipeline_state.json"
        self.events_file = self.pipeline_root / "events" / "events.log"

        # Ensure directories exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.events_file.parent.mkdir(parents=True, exist_ok=True)

    def load_state(self) -> Dict[str, Any]:
        """Load pipeline state"""
        if not self.state_file.exists():
            return {"universes": {}}

        with open(self.state_file, "r") as f:
            return json.load(f)

    def save_state(self, state: Dict[str, Any]):
        """Save pipeline state"""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def get_universes_to_validate(self) -> List[str]:
        """
        Get list of universes that need validation.
        Returns universes where: transformed=true AND validated!=true
        """
        state = self.load_state()
        universes_to_validate = []

        for universe_id, universe_state in state.get("universes", {}).items():
            transformed = universe_state.get("transformed", False)
            validated = universe_state.get("validated", False)

            if transformed and not validated:
                universes_to_validate.append(universe_id)

        return universes_to_validate

    def mark_validated(self, universe_id: str, success: bool = True):
        """
        Mark universe as validated in pipeline state.

        Args:
            universe_id: Universe to mark
            success: Whether validation succeeded
        """
        state = self.load_state()

        if "universes" not in state:
            state["universes"] = {}

        if universe_id not in state["universes"]:
            state["universes"][universe_id] = {}

        # Update state
        state["universes"][universe_id]["validated"] = success
        state["universes"][universe_id]["validated_at"] = datetime.now().isoformat()

        # Save state
        self.save_state(state)

        # Log event
        self._log_event(f"validation {'completed' if success else 'failed'} {universe_id}")

    def _log_event(self, message: str):
        """Append event to events log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event_line = f"{timestamp} {message}\n"

        with open(self.events_file, "a") as f:
            f.write(event_line)

    def get_universe_state(self, universe_id: str) -> Dict[str, Any]:
        """Get state for specific universe"""
        state = self.load_state()
        return state.get("universes", {}).get(universe_id, {})
