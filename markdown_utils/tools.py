"""
Tests and maintains Markdown files containing embedded code listings.
"""
from typing import Optional
import typer
from typing_extensions import Annotated
from markdown_utils import (
    separator,
    check_code_listings,
    check_markdown,
    NumberedFile,
)
from pathlib import Path

app = typer.Typer()


@app.command()
def check():
    """
    Validates Markdown files.
    """
    for tmp_file in Path(".").glob("*.tmp"):
        tmp_file.unlink()
    for md in Path(".").glob("*.md"):
        print(f"{md.name}: [{check_markdown(md)}]")


@app.command()
def listings(
    filename: Annotated[Optional[str], typer.Argument()] = None
):
    """
    Validates code listings within Markdown files.
    """
    print(filename)
    if filename:
        md = Path(filename)
        assert md.exists(), f"{md} does not exist"
        check_code_listings(md)
    else:
        for md in Path(".").glob("*.md"):
            print(separator(md, "+"), end="")
            check_code_listings(md)


@app.command()
def renumber():
    """
    Reorders numbered Markdown files. To insert a file 'n',
    name it 'n.! Chapter Title'. The '!' gives that chapter
    priority over another chapter with the same number.
    """
    chapter_changes = NumberedFile.chapters().changes
    appendix_changes = NumberedFile.appendices().changes
    if not chapter_changes and not appendix_changes:
        print("No Changes")
    for chapter in NumberedFile.chapters().changes:
        # print(chapter)
        print(f"'{chapter.original_name}'  -->  '{chapter.new_name}'")
        # os.rename(chapter.original_name, chapter.new_name)
    for appendix in NumberedFile.appendices().changes:
        # print(appendix)
        print(
            f"'{appendix.original_name}'  -->  '{appendix.new_name}'"
        )
        # os.rename(appendix.original_name, appendix.new_name)


def main():
    app()


if __name__ == "__main__":
    main()
