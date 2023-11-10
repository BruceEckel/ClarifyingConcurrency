import os
import re
from pathlib import Path
import sys
from typing import Generator, Tuple, List
from pprint import pprint


def renumber_files(files: List[Path]) -> Generator[Tuple[str, str], None, None]:
    # Sort files by number while handling missing numbers and the '!' marker
    def file_sort_key(file: Path) -> int:
        match = re.match(r"(\d+)", file.stem)
        return int(match.group(1)) if match else float("inf")

    files_sorted = sorted(files, key=file_sort_key)
    pprint(files_sorted)

    # Find new file position and name
    new_file = None
    for file in files_sorted:
        if "!" in file.stem:
            new_file = file
            break

    if not new_file:
        print("No new file with '!' in its name found.")
        sys.exit()

    # Extract the priority number from the new file name
    priority_match = re.match(r"(\d+)\.!", new_file.stem)
    if not priority_match:
        print(f"'{new_file}' does not have a proper numeric priority.")
        sys.exit()

    priority_number = int(priority_match.group(1))

    # Determine the new numbering for files
    for file in files_sorted:
        current_number_match = re.match(r"(\d+)", file.stem)
        if current_number_match:
            current_number = int(current_number_match.group(1))
            # If this file is the new file, yield its new name without the '!'
            if file == new_file:
                new_file_name = f"{priority_number}. {file.stem.split('! ', 1)[1]}.md"
                yield (file.name, new_file_name)
            # If the current number is greater than or equal to the priority number, increment it
            elif current_number >= priority_number:
                new_number = current_number + 1
                new_file_name = f"{new_number}. {file.stem.split('. ', 1)[1]}.md"
                yield (file.name, new_file_name)


files = list(Path(".").glob("*.md"))
for old_name, new_name in renumber_files(files):
    print(f"Rename '{old_name}' to '{new_name}'")
    os.rename(old_name, new_name)
