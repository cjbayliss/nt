from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import Final

from t2a.types import CodepointRunStarts

PRESENTATION_FORM_REPLACEMENTS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',
        "〝": '"',
        "〞": '"',
        "ʺ": '"',
        "″": '"',
        "‴": "'''",
        "‶": "``",
        "‘": "'",
        "’": "'",
        "‚": "'",
        "‛": "'",
        "ʻ": "'",
        "ʼ": "'",
        "ʽ": "'",
        "ʾ": "'",
        "ʿ": "'",
        "´": "'",
        "ʹ": "'",
        "′": "'",
        "«": "<<",
        "»": ">>",
        "‹": "<",
        "›": ">",
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "–": "-",
        "—": "-",
        "―": "-",
        "−": "-",
        "˗": "-",
        "⁃": "-",
        "➖": "-",
        "﹣": "-",
        "⸺": "--",
        "⸻": "---",
        "…": "...",
        "⋯": "...",
        "‥": "..",
        "\u00ad": "",
        "\u200b": "",
        "\u2060": "",
        "\ufeff": "",
        "ℂ": "C",
        "ℍ": "H",
        "ℊ": "g",
        "ℎ": "h",
        "ℏ": "h",
        "ℐ": "I",
        "ℑ": "I",
        "ℒ": "L",
        "ℓ": "l",
        "ℕ": "N",
        "℘": "P",
        "ℙ": "P",
        "ℚ": "Q",
        "ℛ": "R",
        "ℜ": "R",
        "ℝ": "R",
        "ℤ": "Z",
        "ℨ": "Z",
        "ℬ": "B",
        "ℭ": "C",
        "ℰ": "E",
        "ℱ": "F",
        "ℳ": "M",
        "ℴ": "o",
        "ℋ": "H",
        "ℌ": "H",
    }
)

ASCII_FOLDING_REPLACEMENTS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "ß": "ss",
        "ẞ": "SS",
        "æ": "ae",
        "Æ": "AE",
        "œ": "oe",
        "Œ": "OE",
        "ø": "o",
        "Ø": "O",
        "đ": "d",
        "Đ": "D",
        "ð": "d",
        "Ð": "D",
        "ł": "l",
        "Ł": "L",
        "ħ": "h",
        "Ħ": "H",
        "ŧ": "t",
        "Ŧ": "T",
        "ŋ": "ng",
        "Ŋ": "Ng",
        "þ": "th",
        "Þ": "Th",
        "ı": "i",
        "ŀ": "l",
        "ə": "e",
        "Ə": "E",
        "©": "(c)",
        "®": "(r)",
        "§": "S",
        "†": "*",
        "‡": "*",
        "¢": "c",
        "£": "GBP",
        "€": "EUR",
        "¥": "JPY",
        "⁄": "/",
        "•": "*",
        "‣": "*",
        "∙": "*",
        "‧": "*",
        "◦": "o",
        "·": "*",
        "×": "x",
        "÷": "/",
        "∗": "*",
        "±": "+/-",
        "≈": "~",
        "≤": "<=",
        "≥": ">=",
        "≠": "!=",
        "←": "<-",
        "→": "->",
        "↑": "^",
        "↓": "v",
        "↔": "<->",
        "⇐": "<=",
        "⇒": "=>",
        "⇔": "<=>",
        "➕": "+",
        "➗": "/",
        "➡": "->",
        "⬅": "<-",
        "⬆": "^",
        "⬇": "v",
    }
)


MATHEMATICAL_LETTER_RUN_STARTS: Final[CodepointRunStarts] = (
    0x1D400,
    0x1D434,
    0x1D468,
    0x1D49C,
    0x1D4D0,
    0x1D504,
    0x1D538,
    0x1D56C,
    0x1D5A0,
    0x1D5D4,
    0x1D608,
    0x1D63C,
    0x1D670,
)
MATHEMATICAL_DIGIT_RUN_START: Final[int] = 0x1D7CE
ENCLOSED_NEGATIVE_LETTER_RUN_STARTS: Final[CodepointRunStarts] = (
    0x1F150,
    0x1F170,
)
FULLWIDTH_DIGIT_RUN_START: Final[int] = 0xFF10
FULLWIDTH_UPPERCASE_LETTER_RUN_START: Final[int] = 0xFF21
FULLWIDTH_LOWERCASE_LETTER_RUN_START: Final[int] = 0xFF41
UNICODE_SPACE_CODEPOINTS: Final[tuple[int, ...]] = (
    0x00A0,
    0x202F,
    0x205F,
    0x3000,
    *range(0x2000, 0x200B),
)
DINGBAT_CIRCLED_NUMBER_RUN_START: Final[int] = 0x2776
NEGATIVE_CIRCLED_NUMBER_RUN_START: Final[int] = 0x24EB


def replacements_keyed_by_codepoint(
    character_replacements: Mapping[str, str],
) -> dict[int, str]:
    return {
        ord(character): replacement
        for character, replacement in character_replacements.items()
    }


def mathematical_letter_replacements(
    letter_run_starts: CodepointRunStarts,
) -> dict[int, str]:
    return {
        letter_run_start + letter_offset: chr(
            (65 if letter_offset < 26 else 97) + letter_offset % 26
        )
        for letter_run_start in letter_run_starts
        for letter_offset in range(52)
    }


def mathematical_digit_replacements(digit_run_start: int) -> dict[int, str]:
    return {
        digit_run_start + digit_offset: chr(48 + digit_offset % 10)
        for digit_offset in range(50)
    }


def enclosed_negative_letter_replacements(
    letter_run_starts: CodepointRunStarts,
) -> dict[int, str]:
    return {
        letter_run_start + letter_offset: chr(65 + letter_offset)
        for letter_run_start in letter_run_starts
        for letter_offset in range(26)
    }


def fullwidth_alphanumeric_replacements(
    digit_run_start: int,
    uppercase_letter_run_start: int,
    lowercase_letter_run_start: int,
) -> dict[int, str]:
    return (
        {
            digit_run_start + codepoint_offset: chr(48 + codepoint_offset)
            for codepoint_offset in range(10)
        }
        | {
            uppercase_letter_run_start + codepoint_offset: chr(65 + codepoint_offset)
            for codepoint_offset in range(26)
        }
        | {
            lowercase_letter_run_start + codepoint_offset: chr(97 + codepoint_offset)
            for codepoint_offset in range(26)
        }
    )


def unicode_space_replacements(
    space_codepoints: Iterable[int],
) -> dict[int, str]:
    return {codepoint: " " for codepoint in space_codepoints}


def enclosed_number_replacements(
    dingbat_circled_number_run_start: int,
    negative_circled_number_run_start: int,
) -> dict[int, str]:
    return {
        dingbat_circled_number_run_start + number_offset: str(1 + number_offset)
        for number_offset in range(10)
    } | {
        negative_circled_number_run_start + number_offset: str(11 + number_offset)
        for number_offset in range(10)
    }


NORMALIZATION_TABLE: Final[Mapping[int, str]] = MappingProxyType(
    {
        **replacements_keyed_by_codepoint(PRESENTATION_FORM_REPLACEMENTS),
        **mathematical_letter_replacements(MATHEMATICAL_LETTER_RUN_STARTS),
        **mathematical_digit_replacements(MATHEMATICAL_DIGIT_RUN_START),
        **enclosed_negative_letter_replacements(ENCLOSED_NEGATIVE_LETTER_RUN_STARTS),
        **fullwidth_alphanumeric_replacements(
            FULLWIDTH_DIGIT_RUN_START,
            FULLWIDTH_UPPERCASE_LETTER_RUN_START,
            FULLWIDTH_LOWERCASE_LETTER_RUN_START,
        ),
        **unicode_space_replacements(UNICODE_SPACE_CODEPOINTS),
    }
)

FOLDING_TABLE: Final[Mapping[int, str]] = MappingProxyType(
    {
        **replacements_keyed_by_codepoint(ASCII_FOLDING_REPLACEMENTS),
        **enclosed_number_replacements(
            DINGBAT_CIRCLED_NUMBER_RUN_START,
            NEGATIVE_CIRCLED_NUMBER_RUN_START,
        ),
    }
)

EXPLICITLY_MAPPED_CODEPOINTS: Final[frozenset[int]] = frozenset(
    NORMALIZATION_TABLE
) | frozenset(FOLDING_TABLE)
