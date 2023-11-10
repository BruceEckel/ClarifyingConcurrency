# renumber_files.py
# Uses dataclass ordering to sort, respecting the '!' in the
# filename to mean that file should appear first if there's a conflict.
# So '3.! foo.md' will renumber before '3. bar.md'
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Union, List


@dataclass(order=True)
class NumberedFile:
    # Sorting is based on field order:
    sort_index_1: int = field(init=False)
    sort_index_2: str = field(init=False)
    original_name: str
    text_name: str = field(init=False)  # Without 'n. '
    number: int = field(init=False)
    priority: str = field(init=False)
    new_name: str = field(default="", init=False)

    def __post_init__(self):
        match = re.match(r"(\d+)\.(!)?\s*(.*)", self.original_name)
        if match:
            self.number = int(match.group(1))
            self.priority = "A" if match.group(2) else "B"
            self.text_name = match.group(3).strip()
        else:
            raise ValueError(f"Invalid format for original_name: {self.original_name}")

        self.sort_index_1 = self.number
        self.sort_index_2 = self.priority

    @classmethod
    def sorted_list(cls, path: Union[str, Path] = ".") -> List["NumberedFile"]:
        numbered_files = sorted(
            [
                cls(file.name)
                for file in Path(path).glob("*.md")
                if file.stem[:1].isdigit()
            ]
        )
        for i, nf in enumerate(numbered_files):
            nf.new_name = f"{i}. {nf.text_name}"
        return numbered_files


for nf in NumberedFile.sorted_list():
    if nf.original_name != nf.new_name:
        print(f"rename '{nf.original_name}' to '{nf.new_name}'")
        # os.rename(nf.original_name, nf.new_name)
