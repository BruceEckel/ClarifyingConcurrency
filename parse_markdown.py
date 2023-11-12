# parse_markdown.py
from dataclasses import dataclass
from typing import List
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
        directly by the name of the language
    C.  If there is no language name, then the listing
        represents output from a program.
    """

    language: str | None
    code: str

    def __repr__(self) -> str:
        lang_line = f"```{self.language}\n" if self.language else "```\n"
        return lang_line + self.code + "```\n"

    def __str__(self) -> str:
        # lang_line = f"```{self.language}\n" if self.language else "```\n"
        # return separator("SourceCodeListing") + lang_line + self.code + "\n```"
        return separator("SourceCodeListing") + repr(self)


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


def parse_markdown(
    content: str,
) -> List[MarkdownText | SourceCodeListing | GitHubURL]:
    sections: list[MarkdownText | SourceCodeListing | GitHubURL] = []
    current_text: List[str] = []
    in_code_block = False
    in_github_url = False
    language = None

    for line in content.splitlines(True):  # Keep line endings
        if line.startswith("```"):
            if in_code_block:
                sections.append(SourceCodeListing(language, "".join(current_text)))
                current_text = []
                in_code_block = False
                language = None
            else:
                if current_text:
                    sections.append(MarkdownText("".join(current_text)))
                    current_text = []
                in_code_block = True
                language = line.strip("```").strip() or None
        elif line.startswith("%%"):
            if in_github_url:
                sections.append(GitHubURL("".join(current_text).strip()))
                current_text = []
                in_github_url = False
            else:
                if current_text:
                    sections.append(MarkdownText("".join(current_text)))
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
            sections.append(GitHubURL("".join(current_text).strip()))
        else:
            sections.append(MarkdownText("".join(current_text)))

    return sections
