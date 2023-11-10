# renumber_files.py
# Uses dataclass ordering to sort, respecting the '!' in the
# filename to mean that file should appear first if there's a conflict.
# So '3.! foo.md' will renumber before '3. bar.md'
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Union, List


@dataclass(frozen=True)
class Result:
    files: List["NumberedFile"] = field(default_factory=list)
    changes: List["NumberedFile"] = field(default_factory=list)


@dataclass(order=True)
class NumberedFile:
    # Sorting is based on field order:
    number: int = field(init=False)  # Sort on this first...
    priority: str = field(init=False)  # ... then this
    original_name: str
    appendix: bool = False
    text_name: str = field(init=False)  # Without 'n. '
    new_name: str = field(default="", init=False)

    def __post_init__(self):
        match = re.match(r"(\d+)\.(!)?\s*(.*)", self.original_name)
        if match:
            self.number = int(match.group(1))
            self.priority = "A" if match.group(2) else "B"
            self.text_name = match.group(3).strip()
        else:
            raise ValueError(f"Invalid format: {self.original_name}")

    def __str__(self) -> str:
        br = "\n    "
        return (
            f"NumberedFile{br}"
            f"original_name: '{self.original_name}'{br}"
            f"number: {self.number}{br}"
            f"text_name: '{self.text_name}'{br}"
            f"new_name: '{self.new_name}'{br}"
            f"priority: '{self.priority}'{br}"
            f"appendix: '{self.appendix}'"
        )

    @classmethod
    def chapters(cls, path: Union[str, Path] = ".") -> Result:
        chapter_list = sorted(
            [
                cls(file.name)
                for file in Path(path).glob("*.md")
                if file.stem[:1].isdigit()
            ]
        )
        for i, nf in enumerate(chapter_list):
            nf.new_name = f"{i}. {nf.text_name}"
        changes = [nf for nf in chapter_list if nf.original_name != nf.new_name]
        return Result(chapter_list, changes)

    @classmethod
    def appendices(cls, path: Union[str, Path] = ".") -> Result:
        appendix_list = sorted(
            [
                cls(file.name[1:], appendix=True)
                for file in Path(path).glob("A*.md")
                if file.stem[1:2].isdigit()
            ]
        )
        for i, nf in enumerate(appendix_list):
            nf.original_name = "A" + nf.original_name
            nf.new_name = f"A{i + 1}. {nf.text_name}"  # Start at A1 not A0
        changes = [nf for nf in appendix_list if nf.original_name != nf.new_name]
        return Result(appendix_list, changes)


if __name__ == "__main__":
    for chapter in NumberedFile.chapters().files:
        print(chapter)
        # print(f"'{chapter.original_name}'  -->  '{chapter.new_name}'")
        # os.rename(chapter.original_name, chapter.new_name)
    for appendix in NumberedFile.appendices().files:
        print(appendix)
        # print(f"'{appendix.original_name}'  -->  '{appendix.new_name}'")
        # os.rename(appendix.original_name, appendix.new_name)
