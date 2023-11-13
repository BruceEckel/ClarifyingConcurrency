# parse_markdown.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, List
import re


def separator(id: str, sep_char: str = "-") -> str:
    return f" {id} ".center(60, sep_char) + "\n"


@dataclass
class MarkdownText:
    """
    Contains a section of normal markdown text
    """

    text: str

    def __repr__(self) -> str:
        return f"{self.text}"

    def __str__(self) -> str:
        return separator("MarkdownText") + repr(self)


@dataclass
class SourceCodeListing:
    """
    Contains a single source-code listing:
    A.  All listings begin and end with ``` markers.
    B.  Programming-language listings use ``` followed
        immediately by the name of the language (no space!)
    C.  If it is program output, the name of the language is `text`.
    D.  Providing no language name is not allowed.
    E.  TODO: A `!` after the language name tells the program
        to allow no slug-line, for code fragments that don't have
        an associated file.
    """

    code_block: str
    language: str = ""
    code: str = ""
    ignore: bool = False

    def __post_init__(self):
        lines = self.code_block.splitlines(True)
        tagline = lines[0].strip()
        if tagline.endswith("!"):
            tagline = tagline[:-1]
            self.ignore = True
        self.language = tagline[3:].strip()
        self.code = lines[1:-1]
        assert self.language != "", f"Language cannot be empty in {self.code_block}"

    def __repr__(self) -> str:
        return f"```{self.language}\n" + "".join(self.code) + "```\n"

    def __str__(self) -> str:
        return (
            separator("SourceCodeListing")
            + repr(self)
            + f"{self.language = } {self.ignore = }"
        )


@dataclass
class GitHubURL:
    """
    Contains a URL to a github repo, which is represented in
    the markdown file as:
    %%
    code: URL
    %%
    Each one of these sets the URL for subsequent code listings.
    """

    url: str

    def __repr__(self) -> str:
        return f"%%\ncode: {self.url}\n%%\n"

    def __str__(self) -> str:
        return separator("GitHubURL") + repr(self)


@dataclass
class MarkdownFile:
    original_markdown: str
    contents: List[MarkdownText | SourceCodeListing | GitHubURL]

    def __init__(self, file_path: Path):
        self.original_markdown = file_path.read_text(encoding="utf-8")
        self.contents = []
        current_text: List[str] = []
        in_code_block = False
        in_github_url = False

        for line in self.original_markdown.splitlines(True):
            if line.startswith("```"):
                if in_code_block:  # Complete the code block
                    current_text.append(line)
                    self.contents.append(SourceCodeListing("".join(current_text)))
                    current_text = []
                    in_code_block = False
                else:  # Start a new code block
                    if current_text:
                        self.contents.append(MarkdownText("".join(current_text)))
                        current_text = []
                    in_code_block = True
                    current_text.append(line)
            elif line.startswith("%%"):
                if in_github_url:  # Complete the github URL
                    self.contents.append(GitHubURL("".join(current_text).strip()))
                    current_text = []
                    in_github_url = False
                else:  # Start a new github URL
                    if current_text:
                        self.contents.append(MarkdownText("".join(current_text)))
                        current_text = []
                    in_github_url = True
            elif in_github_url:
                url_match = re.search(r"code:\s*(.*)", line)
                if url_match:
                    current_text.append(url_match.group(1).strip())
            else:
                current_text.append(line)

        if current_text:
            if in_github_url:
                self.contents.append(GitHubURL("".join(current_text).strip()))
            else:
                self.contents.append(MarkdownText("".join(current_text)))

    def __iter__(self) -> Iterator[MarkdownText | SourceCodeListing | GitHubURL]:
        return iter(self.contents)


# Usage example
# markdown_file = MarkdownFile(Path("path/to/markdown/file.md"))
# for section in markdown_file:
#     if isinstance(section, SourceCodeListing):
#         r = check_code_block(section)
#         if r:
#             print(r)
