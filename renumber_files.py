import os
import re
from pathlib import Path
import sys
from typing import Generator, Tuple, List


def renumber_files(files: List[Path]) -> Generator[Tuple[Path, Path], None, None]:
    # Sort files by number while handling missing numbers and the '!' marker
    def file_sort_key(file: Path) -> int:
        match = re.match(r"(\d+)", file.stem)
        return int(match.group(1)) if match else float("inf")

    files_sorted = sorted(files, key=file_sort_key)
    new_files_list = []

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

    # Create a list of tuples for renaming
    for file in files_sorted:
        current_number_match = re.match(r"(\d+)", file.stem)
        if current_number_match:
            current_number = int(current_number_match.group(1))
            if file == new_file:
                # New file takes the priority spot
                new_file_name = f"{priority_number}. {file.stem.split('! ', 1)[1]}.md"
                new_files_list.append((file, file.with_name(new_file_name)))
            elif current_number >= priority_number:
                # Increment the file number
                new_number = current_number + 1
                new_file_name = f"{new_number}. {file.stem.split('. ', 1)[1]}.md"
                new_files_list.append((file, file.with_name(new_file_name)))

    # Yield the new and old names after creating the complete list
    for old_file, new_file in new_files_list:
        yield (old_file, new_file)


files = list(Path(".").glob("*.md"))
renaming_operations = list(renumber_files(files))

# Perform the renaming operations
for old_file, new_file in renaming_operations:
    print(f"Rename '{old_file.name}' to '{new_file.name}'")
    # os.rename(old_file, new_file)

print("Files have been renumbered successfully.")
