# markdown_file.py
from dataclasses import dataclass
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
    E.  A `!` after the language name tells the program
        to allow no slug-line, for code fragments that don't have
        an associated file.
    """

    original_code_block: str
    language: str = ""
    source_file_name: str = ""
    code: str = ""
    ignore: bool = False

    def __post_init__(self):
        lines = self.original_code_block.splitlines(True)
        tagline = lines[0].strip()
        filename_line = lines[1].strip() if len(lines) > 1 else ""

        self.ignore = tagline.endswith("!")
        tagline = tagline.rstrip("!")
        self.language = tagline[3:].strip()
        self.code = "".join(lines[1:-1])

        assert self.language, f"Language cannot be empty in {self.original_code_block}"

        if self.ignore:
            return

        match self.language:
            case "python":
                self._validate_filename(filename_line, "#", ".py")
            case "rust":
                self._validate_filename(filename_line, "//", ".rs")
            case "go":
                self._validate_filename(filename_line, "//", ".go")

    def _validate_filename(self, line: str, comment: str, file_ext: str):
        assert line.startswith(comment) and line.endswith(
            file_ext
        ), f"First line must contain source file name in {self.original_code_block}"
        self.source_file_name = line[len(comment) :].strip()

    def __repr__(self) -> str:
        def ignore_marker():
            return " !" if self.ignore else ""

        return f"```{self.language}{ignore_marker()}\n" + "".join(self.code) + "```\n"

    def __str__(self) -> str:
        return (
            separator("SourceCodeListing")
            + repr(self)
            + f"{self.source_file_name = }\n"
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

    def code_listings(self) -> List[SourceCodeListing]:
        return [part for part in self if isinstance(part, SourceCodeListing)]

    def github_urls(self) -> List[GitHubURL]:
        return [part for part in self if isinstance(part, GitHubURL)]
