from io import StringIO
from pathlib import Path
from parse_markdown import parse_markdown


def test(filename: str):
    content = Path(filename).read_text(encoding="utf-8")
    parsed_sections = parse_markdown(content)

    new_markdown = StringIO()
    new_markdown.write("".join([repr(section) for section in parsed_sections]))
    new_markdown.seek(0)
    if new_markdown.read() == content:
        return "OK"
    else:
        Path(filename + ".tmp").write_text(
            "".join([repr(section) for section in parsed_sections])
        )
        return "Not the same"


for md in Path(".").glob("*.md"):
    print(f"{md.name}: [{test(md.name)}]")
