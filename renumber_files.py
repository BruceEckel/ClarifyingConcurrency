# renumber_files.py
# Uses dataclass ordering to sort, respecting the '!' in the
# filename to mean that file should appear first if there's a conflict.
# So '3.! foo.md' will renumber before '3. bar.md'
import re
import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass(order=True)
class NumberedFile:
    # Sorting occurs based on field order:
    sort_index_1: int = field(init=False)
    sort_index_2: str = field(init=False)
    original_name: str
    text_name: str  # Without 'n. '
    number: int
    priority: str
    new_name: str = ""

    def __post_init__(self):
        self.sort_index_1 = self.number
        self.sort_index_2 = self.priority


def numbered_files():
    results = []
    for file in Path(".").glob("*.md"):
        num = re.match(r"(\d+)\.", file.stem)
        if not num:
            continue
        else:
            file_number = int(num.group(1))
            text_name = file.name
            priority = "B"
            if "!" in text_name:
                priority = "A"
                text_name = text_name.replace("!", "", 1)
            text_name = text_name.split(".", 1)[1].strip()
            results.append(NumberedFile(file.name, text_name, file_number, priority))
    return results


for i, nf in enumerate(sorted(numbered_files())):
    nf.new_name = f"{i}. {nf.text_name}"
    if nf.original_name != nf.new_name:
        print(f"rename '{nf.original_name}' to '{nf.new_name}'")
        os.rename(nf.original_name, nf.new_name)
