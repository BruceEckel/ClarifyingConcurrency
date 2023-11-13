from io import StringIO
from pathlib import Path
from markdown_file import MarkdownFile, SourceCodeListing, separator


def test(md: Path):
    content = md.read_text(encoding="utf-8")
    markdown = MarkdownFile(md)
    new_markdown = StringIO()
    new_markdown.write("".join([repr(section) for section in markdown]))
    new_markdown.seek(0)
    if new_markdown.read() == content:
        return "OK"
    else:
        Path(md.name + ".tmp").write_text(
            "".join([repr(section) for section in markdown])
        )
        return "Not the same"


for md in Path(".").glob("*.md"):
    print(f"{md.name}: [{test(md)}]")
