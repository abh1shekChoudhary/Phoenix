import json
from pathlib import Path
from typing import Dict, Any


class IncidentStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.write_text(json.dumps({}))

    def load_all(self) -> Dict[str, Any]:
        return json.loads(self.path.read_text())

    def save_incident(self, incident_id: str, data: Dict[str, Any]):
        store = self.load_all()
        store[incident_id] = data
        self.path.write_text(json.dumps(store, indent=2))
