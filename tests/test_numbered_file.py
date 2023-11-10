# test_renumber_files.py
import pytest
from ..renumber_files import NumberedFile, Result
from pathlib import Path


# Test Initialization and Parsing
def test_numbered_file_init():
    nf = NumberedFile("3.! example.md")
    assert nf.original_name == "3.! example.md"
    assert nf.number == 3
    assert nf.priority == "A"
    assert nf.text_name == "example.md"

    with pytest.raises(ValueError):
        NumberedFile("invalid.md")


# Test Sorting Order
def test_sorting_order():
    files = [
        NumberedFile("3. bar.md"),
        NumberedFile("2. foo.md"),
        NumberedFile("1.! important.md"),
    ]
    sorted_files = sorted(files)
    assert [nf.original_name for nf in sorted_files] == [
        "1.! important.md",
        "2. foo.md",
        "3. bar.md",
    ]


# Test Chapters Class Method
def test_chapters_method(tmp_path: Path):
    (tmp_path / "1. test.md").touch()
    (tmp_path / "2.! important.md").touch()
    (tmp_path / "3. another.md").touch()

    result = NumberedFile.chapters(path=tmp_path)
    assert isinstance(result, Result)
    assert len(result.files) == 3
    assert result.files[0].new_name == "0. test.md"


# Test Appendices Class Method
def test_appendices_method(tmp_path: Path):
    (tmp_path / "A1. appendix1.md").touch()
    (tmp_path / "A2. appendix2.md").touch()
    (tmp_path / "A3. appendix3.md").touch()

    result = NumberedFile.appendices(path=tmp_path)
    assert isinstance(result, Result)
    assert len(result.files) == 3
    assert result.files[0].new_name == "A1. appendix1.md"
