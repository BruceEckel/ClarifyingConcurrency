from pathlib import Path
from typing import Generator, Tuple
import re
from pprint import pprint
from dataclasses import dataclass, field
import operator


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

# def renumber_files(directory: Path) -> Generator[Tuple[str, str], None, None]:
#     # Gather all files and sort by name
#     files = sorted(directory.glob("*.md"), key=lambda f: f.stem)
#     pprint(files)
#     pivot_file = None
#     pivot_number = None

#     # Find the pivot file and determine the pivot number
#     for file in files:
#         if "!" in file.stem:
#             pivot_file = file
#             pivot_number = int(re.match(r"(\d+)\.!", file.stem).group(1))
#             break

#     if pivot_file is None:
#         raise ValueError("No pivot file with '!' in its name found.")

#     # Generate new file names up to the pivot
#     for i, file in enumerate(files[: files.index(pivot_file)]):
#         new_name = f"{i}. {file.stem.split('. ', 1)[1]}.md"
#         yield (file.name, new_name)

#     # Generate new name for the pivot file
#     new_pivot_name = f"{pivot_number}. {pivot_file.stem.split('! ', 1)[1]}.md"
#     yield (pivot_file.name, new_pivot_name)

#     # Generate new file names after the pivot
#     start_after_pivot = pivot_number + 1
#     for i, file in enumerate(
#         files[files.index(pivot_file) + 1 :], start=start_after_pivot
#     ):
#         new_name = f"{i}. {file.stem.split('. ', 1)[1]}.md"
#         yield (file.name, new_name)


# # Example usage
# for old_name, new_name in renumber_files(Path(".")):
#     print(f"Rename '{old_name}' to '{new_name}'")
#     # Uncomment the line below to actually perform the renaming
#     # os.rename(directory_path / old_name, directory_path / new_name)
