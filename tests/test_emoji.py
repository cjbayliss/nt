from typing import Any

from nt.emoji import (
    EMOJI_CODEPOINT_RANGES,
    EMOJI_MAPPED_CODEPOINTS,
    EMOJI_RUN_PATTERN,
    codepoint_intervals_as_character_class,
    codepoints_as_character_class,
)
from nt.tables import EXPLICITLY_MAPPED_CODEPOINTS


def emoji_pattern_groupdict(text: str) -> dict[str, Any]:
    pattern_match = EMOJI_RUN_PATTERN.fullmatch(text)
    assert pattern_match is not None
    return pattern_match.groupdict()


def test_codepoint_intervals_as_character_class_formats_every_interval() -> None:
    assert (
        codepoint_intervals_as_character_class(((0x41, 0x5A), (0x1F600, 0x1F64F)))
        == "\\U00000041-\\U0000005A\\U0001F600-\\U0001F64F"
    )


def test_codepoints_as_character_class_sorts_the_given_codepoints() -> None:
    assert (
        codepoints_as_character_class({0x5A, 0x41, 0x30})
        == "\\U00000030\\U00000041\\U0000005A"
    )


def test_emoji_codepoint_ranges_are_sorted_and_non_overlapping() -> None:
    assert all(start <= end for start, end in EMOJI_CODEPOINT_RANGES)
    assert all(
        EMOJI_CODEPOINT_RANGES[index][1] < EMOJI_CODEPOINT_RANGES[index + 1][0]
        for index in range(len(EMOJI_CODEPOINT_RANGES) - 1)
    )


def test_emoji_mapped_codepoints_are_mapped_codepoints_inside_emoji_ranges() -> None:
    assert (
        frozenset(
            codepoint
            for codepoint in EXPLICITLY_MAPPED_CODEPOINTS
            if any(start <= codepoint <= end for start, end in EMOJI_CODEPOINT_RANGES)
        )
        == EMOJI_MAPPED_CODEPOINTS
    )
    assert 0x27A1 in EMOJI_MAPPED_CODEPOINTS
    assert 0x1F600 not in EMOJI_MAPPED_CODEPOINTS


def test_emoji_run_pattern_matches_single_codepoint_emoji_as_a_run() -> None:
    assert emoji_pattern_groupdict("😀") == {
        "emoji_run": "😀",
        "single_character": None,
    }


def test_emoji_run_pattern_matches_plain_text_as_single_characters() -> None:
    assert emoji_pattern_groupdict("a") == {
        "emoji_run": None,
        "single_character": "a",
    }


def test_emoji_run_pattern_matches_multi_codepoint_emoji_as_one_run() -> None:
    for emoji_run in ("🇺🇸", "👨‍👩‍👧‍👦", "❤️", "👋🏽"):
        assert emoji_pattern_groupdict(emoji_run)["emoji_run"] == emoji_run
        assert emoji_pattern_groupdict(emoji_run)["single_character"] is None


def test_emoji_run_pattern_does_not_start_runs_on_explicitly_mapped_codepoints() -> (
    None
):
    assert emoji_pattern_groupdict("➖") == {
        "emoji_run": None,
        "single_character": "➖",
    }


def test_emoji_run_pattern_splits_text_emoji_text_into_three_matches() -> None:
    matched_groups = [
        pattern_match.groupdict()
        for pattern_match in EMOJI_RUN_PATTERN.finditer("a😀b")
    ]
    assert [groups["emoji_run"] for groups in matched_groups] == [None, "😀", None]
    assert [groups["single_character"] for groups in matched_groups] == ["a", None, "b"]


def test_emoji_run_pattern_matches_newlines_as_single_characters() -> None:
    assert emoji_pattern_groupdict("\n") == {
        "emoji_run": None,
        "single_character": "\n",
    }
