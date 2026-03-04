"""Pipeline state management for multi-engine coordination."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class PipelineState:
    """Manages shared pipeline state across engines."""

    def __init__(self, pipeline_root: Path) -> None:
        self.state_file = pipeline_root / "state" / "pipeline_state.json"
        self.events_log = pipeline_root / "events" / "events.log"

        # Ensure directories exist
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.events_log.parent.mkdir(parents=True, exist_ok=True)

        # Initialize state file if it doesn't exist
        if not self.state_file.exists():
            self._write_state({"universes": {}})

    def _read_state(self) -> dict[str, Any]:
        """Read current pipeline state."""
        with open(self.state_file) as f:
            return json.load(f)

    def _write_state(self, state: dict[str, Any]) -> None:
        """Write pipeline state."""
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def mark_parsed(self, universe_id: str) -> None:
        """
        Mark a universe as successfully parsed.

        Only modifies the 'parsed' flag - never touches 'transformed' or 'validated'.

        Args:
            universe_id: Universe identifier
        """
        state = self._read_state()

        # Ensure universe entry exists
        if universe_id not in state["universes"]:
            state["universes"][universe_id] = {
                "parsed": False,
                "transformed": False,
                "validated": False,
            }

        # Set parsed = true (only modify this field)
        state["universes"][universe_id]["parsed"] = True

        # Write updated state
        self._write_state(state)

        # Log event
        self._log_event(f"parser completed {universe_id}")

    def _log_event(self, message: str) -> None:
        """
        Append event to events.log.

        Args:
            message: Event message to log
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        event_line = f"{timestamp} {message}\n"

        with open(self.events_log, "a") as f:
            f.write(event_line)

    def get_universe_state(self, universe_id: str) -> dict[str, bool] | None:
        """
        Get state for a specific universe.

        Args:
            universe_id: Universe identifier

        Returns:
            Universe state dict or None if not found
        """
        state = self._read_state()
        return state["universes"].get(universe_id)

    def is_parsed(self, universe_id: str) -> bool:
        """
        Check if universe has been parsed.

        Args:
            universe_id: Universe identifier

        Returns:
            True if universe is marked as parsed
        """
        universe_state = self.get_universe_state(universe_id)
        return universe_state.get("parsed", False) if universe_state else False
