import json
from pathlib import Path
from datetime import datetime
from statistics import mean


class FixHistoryRegistry:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.data = self._load()

    # ---------------------------------------

    def _load(self):
        if not self.storage_path.exists():
            return {}

        try:
            return json.loads(self.storage_path.read_text())
        except Exception:
            return {}

    def _save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(self.data, indent=2))

    # ---------------------------------------

    def record_attempt(self, failure_fp: str, fix_fp: str, timestamp: float):
        failure_record = self.data.setdefault(failure_fp, {})
        fix_record = failure_record.setdefault(fix_fp, {
            "attempts": 0,
            "failures": 0,
            "successes": 0,
            "ttf_samples": [],
            "last_attempt_at": None
        })

        fix_record["attempts"] += 1
        fix_record["last_attempt_at"] = timestamp
        self._save()

    # ---------------------------------------

    def record_failure(self, failure_fp: str, fix_fp: str, time_to_failure: float):
        if failure_fp not in self.data:
            return

        if fix_fp not in self.data[failure_fp]:
            return

        record = self.data[failure_fp][fix_fp]
        record["failures"] += 1
        record["ttf_samples"].append(time_to_failure)
        self._save()

    # ---------------------------------------

    def record_success(self, failure_fp: str, fix_fp: str):
        if failure_fp not in self.data:
            return

        if fix_fp not in self.data[failure_fp]:
            return

        record = self.data[failure_fp][fix_fp]
        record["successes"] += 1
        self._save()

    # ---------------------------------------

    def get_stats(self, failure_fp: str, fix_fp: str):
        if failure_fp not in self.data:
            return None

        if fix_fp not in self.data[failure_fp]:
            return None

        record = self.data[failure_fp][fix_fp]

        avg_ttf = None
        if record["ttf_samples"]:
            avg_ttf = mean(record["ttf_samples"])

        success_rate = 0
        if record["attempts"] > 0:
            success_rate = record["successes"] / record["attempts"]

        return {
            "attempts": record["attempts"],
            "failures": record["failures"],
            "successes": record["successes"],
            "avg_time_to_failure": avg_ttf,
            "success_rate": success_rate
        }
