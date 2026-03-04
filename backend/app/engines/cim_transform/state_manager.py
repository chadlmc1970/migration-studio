"""Pipeline State Manager"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class PipelineState:
    """Manages pipeline state file for coordinating engines"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load pipeline state from file"""
        if not self.state_file.exists():
            return {"universes": {}}

        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                # Ensure universes key exists
                if "universes" not in data:
                    data["universes"] = {}
                return data
        except (json.JSONDecodeError, IOError):
            return {"universes": {}}

    def save_state(self):
        """Save pipeline state to file"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def needs_transformation(self, universe_id: str) -> bool:
        """Check if universe needs transformation"""
        universes = self.state.get("universes", {})

        if universe_id not in universes:
            return False

        universe_state = universes[universe_id]
        parsed = universe_state.get('parsed', False)
        transformed = universe_state.get('transformed', False)

        return parsed and not transformed

    def mark_transformed(self, universe_id: str):
        """Mark universe as transformed"""
        if "universes" not in self.state:
            self.state["universes"] = {}

        if universe_id not in self.state["universes"]:
            self.state["universes"][universe_id] = {
                "parsed": False,
                "transformed": False,
                "validated": False
            }

        self.state["universes"][universe_id]['transformed'] = True
        self.save_state()

    def get_all_universes_needing_transform(self) -> list[str]:
        """Get all universe IDs that need transformation"""
        universes = self.state.get("universes", {})
        return [
            uid for uid in universes.keys()
            if self.needs_transformation(uid)
        ]


class EventLogger:
    """Logs pipeline events"""

    def __init__(self, events_file: Path):
        self.events_file = events_file
        self.events_file.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, universe_id: str, details: str = ""):
        """Log a pipeline event"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        message = f"{timestamp} {event_type} {universe_id}"
        if details:
            message += f" {details}"

        with open(self.events_file, 'a') as f:
            f.write(message + "\n")
