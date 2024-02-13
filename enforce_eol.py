#!/usr/bin/env python
import subprocess
import sys
import warnings
from collections.abc import Iterator
from pathlib import Path
from traceback import print_exc


def assert_eol_characters(filename: Path) -> None:
    size = filename.stat().st_size
    if size == 0:
        return
    if size == 1:
        msg = f"File {filename} contains only a single character"
        raise ValueError(msg)
    with filename.open("rb+") as file:
        file.seek(-2, 2)
        penultimate, last = file.read(2)
    newline = ord("\n")
    if last != newline:
        msg = f"File {filename} doesn't end with a \\n character"
        raise ValueError(msg)
    if penultimate == newline:
        msg = f"File {filename} ends with multiple \\n characters"
        raise ValueError(msg)


def gather_files() -> Iterator[Path]:
    ignored_suffixes = {".ico", ".jpg", ".png"}
    stdout = subprocess.check_output(["git", "ls-files"])  # noqa: S603,S607
    for filename in stdout.decode().split("\n"):
        if not filename:
            continue
        file = Path(__file__).parent.joinpath(filename)
        if file.suffix not in ignored_suffixes:
            yield file


def main() -> None:
    failed = False
    for file in gather_files():
        try:
            assert_eol_characters(file)
        except ValueError:
            print_exc(limit=0)
            failed = True
        except FileNotFoundError:
            warnings.warn(
                f"File {file} not found. If it was recently deleted, please stage it first.",
                RuntimeWarning,
                stacklevel=3,
            )
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
