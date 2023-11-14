# check_code_listings.py
from pathlib import Path
from .markdown_file import MarkdownFile, SourceCodeListing, separator


def check_code_block(scl: SourceCodeListing) -> str | None:
    if scl.language == "text" or scl.ignore:
        return None
    return f"{scl.language}: {scl.source_file_name}"


def check_code_listings(md: Path):
    for listing in MarkdownFile(md).code_listings():
        assert isinstance(listing, SourceCodeListing)
        r = check_code_block(listing)
        if r:
            print(r)


if __name__ == "__main__":
    for md in Path(".").glob("*.md"):
        print(separator(md.name, "+"), end="")
        check_code_listings(md)
