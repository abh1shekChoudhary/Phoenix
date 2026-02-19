from pathlib import Path
from typing import List

def read_java_file(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()
