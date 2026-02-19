import json
from pathlib import Path
from typing import Dict


class StrategyPerformanceRepository:
    """
    Stores historical performance of strategies per failure fingerprint.

    Data format:

    {
        "<fingerprint>|V1": {
            "success": int,
            "fail": int
        }
    }
    """

    def __init__(self, path: Path):
        self.path = path
        self.data: Dict[str, Dict[str, int]] = {}
        self._load()

    # -----------------------------------------------------

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    # -----------------------------------------------------

    def _persist(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    # -----------------------------------------------------

    def record(self, fingerprint: str, strategy_version: int, success: bool):
        """
        Records outcome of a strategy execution.
        """

        if not fingerprint:
            return

        key = f"{fingerprint}|V{strategy_version}"

        if key not in self.data:
            self.data[key] = {"success": 0, "fail": 0}

        if success:
            self.data[key]["success"] += 1
        else:
            self.data[key]["fail"] += 1

        self._persist()

    # -----------------------------------------------------

    def get_stats(self, fingerprint: str, strategy_version: int):
        key = f"{fingerprint}|V{strategy_version}"
        return self.data.get(key, {"success": 0, "fail": 0})

    def get_all_for_fingerprint(self, fingerprint: str) -> dict:
        """
        Returns:
            {
                1: {"success": X, "fail": Y},
                2: {"success": A, "fail": B}
            }
        """
        result = {}

        for key, value in self.data.items():
            fp, version = key.split("|")
            if fp == fingerprint:
                version_num = int(version.replace("V", ""))
                result[version_num] = value

        return result
    
    def get_stats_for_fingerprint(self, fingerprint: str):
        return {
            k: v
            for k, v in self.data.items()
            if k.startswith(fingerprint)
        }

