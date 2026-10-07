import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from nt.emoji import EMOJI_RUN_PATTERN
from nt.tables import FOLDING_TABLE, NORMALIZATION_TABLE


@dataclass(frozen=True)
class ConversionTables:
    normalization_table: Mapping[int, str]
    folding_table: Mapping[int, str]
    emoji_run_pattern: re.Pattern[str]


DEFAULT_CONVERSION_TABLES: Final[ConversionTables] = ConversionTables(
    normalization_table=NORMALIZATION_TABLE,
    folding_table=FOLDING_TABLE,
    emoji_run_pattern=EMOJI_RUN_PATTERN,
)


def convert(
    text: str,
    *,
    conversion_tables: ConversionTables = DEFAULT_CONVERSION_TABLES,
    level: int = 0,
    replacement: str = "",
    keep_emoji: bool = False,
) -> str:
    if not 0 <= level <= 2:
        raise ValueError(f"level must be 0, 1 or 2, got {level!r}")
    if text.isascii():
        return text
    if keep_emoji:
        return convert_preserving_emoji_runs(
            text, conversion_tables, level, replacement
        )
    return convert_without_emoji_preservation(
        text, conversion_tables, level, replacement
    )


def convert_without_emoji_preservation(
    text: str,
    conversion_tables: ConversionTables,
    level: int,
    replacement: str,
) -> str:
    normalized_text = text.translate(conversion_tables.normalization_table)
    if level == 0:
        return normalized_text
    decomposed_text = "".join(
        character
        for character in unicodedata.normalize("NFKD", normalized_text)
        if not unicodedata.category(character).startswith("M")
    )
    refolded_text = decomposed_text.translate(
        conversion_tables.folding_table
    ).translate(conversion_tables.normalization_table)
    if level == 1:
        return refolded_text
    if replacement:
        return "".join(
            character if character.isascii() else replacement
            for character in refolded_text
        )
    return refolded_text.encode("ascii", "ignore").decode("ascii")


def convert_preserving_emoji_runs(
    text: str,
    conversion_tables: ConversionTables,
    level: int,
    replacement: str,
) -> str:
    return "".join(
        convert_pattern_match(pattern_match, conversion_tables, level, replacement)
        for pattern_match in conversion_tables.emoji_run_pattern.finditer(text)
    )


def convert_pattern_match(
    pattern_match: re.Match[str],
    conversion_tables: ConversionTables,
    level: int,
    replacement: str,
) -> str:
    matched_groups = pattern_match.groupdict()
    emoji_run = matched_groups["emoji_run"]
    single_character = matched_groups["single_character"]
    return (
        emoji_run
        if emoji_run
        else convert_without_emoji_preservation(
            single_character, conversion_tables, level, replacement
        )
    )


def to_ascii(
    text: str,
    *,
    conversion_tables: ConversionTables = DEFAULT_CONVERSION_TABLES,
    level: int = 0,
    replacement: str = "",
    keep_emoji: bool = False,
) -> str:
    return convert(
        text,
        conversion_tables=conversion_tables,
        level=level,
        replacement=replacement,
        keep_emoji=keep_emoji,
    )
