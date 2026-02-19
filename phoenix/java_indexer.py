from pathlib import Path
from typing import Dict

class JavaProjectIndex:
    def __init__(self, root: Path):
        self.root = root
        self.files: Dict[str, Path] = {}

    def build(self):
        src_dir = self.root / "src" / "main" / "java"
        if not src_dir.exists():
            return

        for path in src_dir.rglob("*.java"):
            self.files[path.name] = path

    def find(self, filename: str) -> Path | None:
        return self.files.get(filename)
