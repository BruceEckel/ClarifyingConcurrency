# check_code_listings.py
from pathlib import Path
from markdown_file import MarkdownFile, SourceCodeListing, separator


def check_code_block(scl: SourceCodeListing) -> str | None:
    first_line = scl.code[0]
    err_msg = f"{scl.language} ----> {first_line}"

    match scl.language:
        case None:
            return err_msg
        case "rust":
            if first_line.startswith("//") and first_line.endswith(".rs"):
                return None
            return err_msg
        case "python":
            if first_line.startswith("#") and first_line.endswith(".py"):
                return None
            return err_msg
        case "text":
            return None
        case _:
            return err_msg


def check_code_listings(md: Path):
    markdown = MarkdownFile(md)
    for section in markdown:
        if isinstance(section, SourceCodeListing):
            r = check_code_block(section)
            if r:
                print(r)


for md in Path(".").glob("*.md"):
    print(separator(md, "+"))
    check_code_listings(md)
