import yaml
from pathlib import Path

class PhoenixConfig:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        self.data = self._load()

    def _load(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Config not found: {self.path}")

        with open(self.path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, *keys, default=None):
        current = self.data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current
