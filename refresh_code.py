# refresh_code.py
from pathlib import Path
from typing import List, Tuple
import re


def code_url_tags(file_path: Path) -> List[str]:
    pattern = r"%%\s*code:\s*(https://github\.com/BruceEckel/python-experiments/tree/main/.+)\s*%%"
    return re.findall(pattern, file_path.read_text(encoding="utf-8"))


def local_code(urls: List[str], base_path: str) -> List[Path]:
    return [
        Path(
            url.replace(
                "https://github.com/BruceEckel/python-experiments/tree/main", base_path
            )
        )
        for url in urls
    ]


def python_code(file_path: Path, base_path: str) -> List[Tuple[str, Path]]:
    blocks = re.findall(
        r"```python\s*# (.*\.py)\s", file_path.read_text(encoding="utf-8")
    )
    return [(block, Path(base_path) / block) for block in blocks]


def verify_files_exist(file_paths: List[Path]) -> List[bool]:
    return [file_path.exists() for file_path in file_paths]


if __name__ == "__main__":
    base_path = "C:/git/python-experiments"

    for file_path in Path(__file__).parent.glob("*.md"):
        urls = code_url_tags(file_path)
        local_paths = local_code(urls, base_path)

        for name, path in python_code(file_path, base_path):
            if path.exists():
                print(f"Verified: {path}")
            else:
                print(f"Missing: {path}")
