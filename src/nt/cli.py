import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from importlib.metadata import version
from typing import TextIO

from nt.conversion import convert


@dataclass(frozen=True)
class ConversionRequest:
    level: int
    replacement: str
    keep_emoji: bool


def build_argument_parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(
        prog="nt",
        description=(
            "Convert text so it reads well in terminals: quotes, dashes, "
            "styled Unicode fonts, ... while keeping everything else."
        ),
        epilog=(
            "levels:\n"
            "  0  normalize (default): fix quotes/dashes/ellipsis/styled\n"
            "     fonts/fullwidth letters; keep everything else as-is\n"
            "  1  fold: also strip accents and fold ligatures, fractions,\n"
            "     numerals and symbols towards ASCII\n"
            "  2  strict: output pure ASCII; drop (or -r) anything unmapped"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    argument_parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="input files ('-' for stdin; default: stdin)",
    )
    argument_parser.add_argument(
        "-l",
        "--level",
        type=int,
        choices=(0, 1, 2),
        default=0,
        help="conversion level (default: 0)",
    )
    argument_parser.add_argument(
        "-r",
        "--replace",
        dest="replacement",
        default="",
        metavar="TEXT",
        help=(
            "level 2 only: replacement for non-ASCII characters that have "
            "no mapping (default: drop them)"
        ),
    )
    argument_parser.add_argument(
        "--keep-emoji",
        action="store_true",
        help=(
            "keep emoji runs verbatim (at level 2, keeps emoji instead of "
            "dropping them)"
        ),
    )
    argument_parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('nt')}",
    )
    return argument_parser


def convert_stream_lines(
    input_stream: TextIO,
    output_stream: TextIO,
    conversion_request: ConversionRequest,
) -> None:
    output_stream.writelines(
        convert(
            line,
            level=conversion_request.level,
            replacement=conversion_request.replacement,
            keep_emoji=conversion_request.keep_emoji,
        )
        for line in input_stream
    )


def convert_input_file(
    input_file_name: str,
    input_stream: TextIO,
    output_stream: TextIO,
    conversion_request: ConversionRequest,
) -> OSError | None:
    if input_file_name == "-":
        convert_stream_lines(input_stream, output_stream, conversion_request)
        return None
    try:
        with open(input_file_name, encoding="utf-8", errors="replace") as input_file:
            convert_stream_lines(input_file, output_stream, conversion_request)
    except OSError as encountered_error:
        return encountered_error
    return None


def main(command_line_arguments: list[str] | None = None) -> int:
    argument_parser = build_argument_parser()
    arguments = argument_parser.parse_args(command_line_arguments)
    conversion_request = ConversionRequest(
        level=arguments.level,
        replacement=arguments.replacement,
        keep_emoji=arguments.keep_emoji,
    )
    input_file_names: Sequence[str] = arguments.files or ("-",)
    for input_file_name in input_file_names:
        encountered_error = convert_input_file(
            input_file_name, sys.stdin, sys.stdout, conversion_request
        )
        if encountered_error is not None:
            print(f"nt: {encountered_error}", file=sys.stderr)
            return 1
    return 0
