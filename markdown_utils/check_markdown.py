# check_markdown.py
from io import StringIO
from pathlib import Path
from .markdown_file import MarkdownFile


def check_markdown(md: Path):
    markdown = MarkdownFile(md)
    for ghurl in markdown.github_urls():
        print(f"GitHubURL: {ghurl.url}")
    new_markdown = StringIO()
    new_markdown.write("".join([repr(section) for section in markdown]))
    new_markdown.seek(0)
    if new_markdown.read() == md.read_text(encoding="utf-8"):
        return "OK"
    else:
        Path(md.name + ".tmp").write_text(
            "".join([repr(section) for section in markdown])
        )
        return "Not the same"


if __name__ == "__main__":
    for tmp_file in Path(".").glob("*.tmp"):
        tmp_file.unlink()
    for md in Path(".").glob("*.md"):
        print(f"{md.name}: [{check_markdown(md)}]")
