from pathlib import Path
import re
from dataclasses import dataclass, field
import os


@dataclass(order=True)
class NumberedFile:
    sort_index_1: int = field(init=False)
    sort_index_2: str = field(init=False)
    original_name: str
    text_name: str
    number: int
    priority: str
    new_name: str = ""

    def __post_init__(self):
        self.sort_index_1 = self.number
        self.sort_index_2 = self.priority


original_files = Path(".").glob("*.md")
numbered_files = []
for file in original_files:
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
        numbered_files.append(NumberedFile(file.name, text_name, file_number, priority))

for i, nf in enumerate(sorted(numbered_files)):
    nf.new_name = f"{i}. {nf.text_name}"
    if nf.original_name != nf.new_name:
        print(f"rename '{nf.original_name}' to '{nf.new_name}'")
        os.rename(nf.original_name, nf.new_name)
