from typing import Final

from hypothesis import given
from hypothesis import strategies as st

from nt.conversion import convert, to_ascii
from nt.emoji import (
    EMOJI_CODEPOINT_RANGES,
    EMOJI_COMPONENT_CODEPOINT_RANGES,
    EMOJI_RUN_PATTERN,
)

CONVERSION_LEVELS: Final[tuple[int, int, int]] = (0, 1, 2)

CONVERSION_LEVEL: Final[st.SearchStrategy[int]] = st.sampled_from(CONVERSION_LEVELS)

ARBITRARY_TEXT: Final[st.SearchStrategy[str]] = st.text()

ASCII_TEXT: Final[st.SearchStrategy[str]] = st.text(
    alphabet=st.characters(min_codepoint=0, max_codepoint=0x7F)
)

ASCII_REPLACEMENT: Final[st.SearchStrategy[str]] = st.text(
    alphabet=st.characters(min_codepoint=0x20, max_codepoint=0x7E),
    max_size=4,
)

CODEPOINT_CHARACTERS: Final[st.SearchStrategy[str]] = (
    st.sampled_from(EMOJI_CODEPOINT_RANGES + EMOJI_COMPONENT_CODEPOINT_RANGES)
    .flatmap(
        lambda codepoint_interval: st.sampled_from(
            range(codepoint_interval[0], codepoint_interval[1] + 1)
        )
    )
    .map(chr)
)

TEXT_WITH_EMOJI_RUNS: Final[st.SearchStrategy[str]] = st.lists(
    st.one_of(st.characters(), CODEPOINT_CHARACTERS),
    max_size=32,
).map("".join)


def emoji_runs_of(text: str) -> list[str]:
    return [
        pattern_match.group("emoji_run")
        for pattern_match in EMOJI_RUN_PATTERN.finditer(text)
        if pattern_match.group("emoji_run")
    ]


def non_emoji_text_of(text: str) -> str:
    return "".join(
        single_character
        for pattern_match in EMOJI_RUN_PATTERN.finditer(text)
        if (single_character := pattern_match.group("single_character")) is not None
    )


@given(text=ASCII_TEXT, level=CONVERSION_LEVEL, replacement=ASCII_REPLACEMENT)
def test_convert_returns_ascii_text_unchanged_for_any_level_and_replacement(
    text: str,
    level: int,
    replacement: str,
) -> None:
    assert convert(text, level=level, replacement=replacement, keep_emoji=True) == text
    assert convert(text, level=level, replacement=replacement) == text


@given(
    text=TEXT_WITH_EMOJI_RUNS,
    level=CONVERSION_LEVEL,
    keep_emoji=st.booleans(),
    replacement=ASCII_REPLACEMENT,
)
def test_convert_is_idempotent_at_every_level(
    text: str,
    level: int,
    keep_emoji: bool,
    replacement: str,
) -> None:
    converted_once = convert(
        text, level=level, keep_emoji=keep_emoji, replacement=replacement
    )
    converted_twice = convert(
        converted_once, level=level, keep_emoji=keep_emoji, replacement=replacement
    )
    assert converted_twice == converted_once


@given(text=ARBITRARY_TEXT, replacement=ASCII_REPLACEMENT)
def test_level_two_output_is_pure_ascii_without_emoji_preservation(
    text: str,
    replacement: str,
) -> None:
    assert convert(text, level=2, replacement=replacement).isascii()


@given(text=TEXT_WITH_EMOJI_RUNS, replacement=ASCII_REPLACEMENT)
def test_level_two_with_emoji_preservation_keeps_only_emoji_runs_outside_ascii(
    text: str,
    replacement: str,
) -> None:
    converted_text = convert(text, level=2, replacement=replacement, keep_emoji=True)
    assert non_emoji_text_of(converted_text).isascii()


@given(text=TEXT_WITH_EMOJI_RUNS, level=CONVERSION_LEVEL)
def test_emoji_preservation_keeps_every_input_emoji_run_verbatim(
    text: str,
    level: int,
) -> None:
    converted_text = convert(text, level=level, keep_emoji=True)
    assert all(emoji_run in converted_text for emoji_run in emoji_runs_of(text))


@given(
    text=TEXT_WITH_EMOJI_RUNS,
    level=CONVERSION_LEVEL,
    keep_emoji=st.booleans(),
    replacement=ASCII_REPLACEMENT,
)
def test_to_ascii_returns_the_same_result_as_convert(
    text: str,
    level: int,
    keep_emoji: bool,
    replacement: str,
) -> None:
    assert to_ascii(
        text, level=level, replacement=replacement, keep_emoji=keep_emoji
    ) == convert(text, level=level, replacement=replacement, keep_emoji=keep_emoji)
