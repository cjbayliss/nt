from typing import Any

import pytest

from nt.conversion import (
    DEFAULT_CONVERSION_TABLES,
    ConversionTables,
    convert,
    to_ascii,
)
from nt.emoji import EMOJI_RUN_PATTERN
from nt.tables import FOLDING_TABLE, NORMALIZATION_TABLE


def test_convert_rejects_levels_outside_zero_one_and_two() -> None:
    for invalid_level in (-1, 3, 42):
        with pytest.raises(ValueError, match="level must be 0, 1 or 2"):
            convert("café", level=invalid_level)


def test_convert_returns_ascii_text_unchanged_at_every_level() -> None:
    for level in (0, 1, 2):
        assert (
            convert("Hello, World! 123\n\t", level=level, replacement="?")
            == "Hello, World! 123\n\t"
        )


def test_convert_returns_the_empty_string_unchanged() -> None:
    assert convert("", level=2, replacement="?") == ""


def test_level_zero_normalizes_quotes_dashes_and_ellipsis() -> None:
    assert convert("“x”") == '"x"'
    assert convert("‘a’") == "'a'"
    assert convert("—–‒―‐‑−") == "-------"
    assert convert("…") == "..."
    assert convert("«‹x›»") == "<<<x>>>"


def test_level_zero_normalizes_styled_mathematical_letters_and_digits() -> None:
    assert convert("𝐀𝐛𝐜 𝟏𝟐𝟑") == "Abc 123"
    assert convert("ℕℝℤℂ") == "NRZC"
    assert convert("🅰") == "A"
    assert convert("ＡＢＣ１２３") == "ABC123"
    assert convert("ｆｕｌｌｗｉｄｔｈ") == "fullwidth"


def test_level_zero_normalizes_unicode_spaces_and_invisible_characters() -> None:
    assert convert("\u00a0x\u2003y\u3000") == " x y "
    assert convert("a\u00adb\u200bc\u2060d\ufeff") == "abcd"


def test_level_zero_leaves_accents_fractions_and_symbols_alone() -> None:
    assert convert("café") == "café"
    assert convert("½ ¾") == "½ ¾"
    assert convert("© ± ≈") == "© ± ≈"


def test_level_one_strips_accents_and_expands_ligatures() -> None:
    assert convert("Crème brûlée", level=1) == "Creme brulee"
    assert convert("naïve façade", level=1) == "naive facade"
    assert convert("ﬁﬂ", level=1) == "fifl"


def test_level_one_folds_special_letters_towards_ascii() -> None:
    assert (
        convert("Straße, Ø, Œ, Ł, Đ, Þ, ß", level=1) == "Strasse, O, OE, L, D, Th, ss"
    )


def test_level_one_expands_fractions_and_superscripts_via_decomposition() -> None:
    assert convert("½ ¼ ¾", level=1) == "1/2 1/4 3/4"
    assert convert("²³", level=1) == "23"


def test_level_one_folds_circled_numbers_bullets_and_currency() -> None:
    assert convert("\u2776 \u24eb", level=1) == "1 11"
    assert convert("• point", level=1) == "* point"
    assert convert("€100 £5", level=1) == "EUR100 GBP5"


def test_level_one_folds_comparison_and_arrow_symbols() -> None:
    assert convert("± ≈ ≠ ≤ ≥ × ÷", level=1) == "+/- ~ = <= >= x /"
    assert convert("← → ↔ ⇒", level=1) == "<- -> <-> =>"


def test_level_one_folds_box_drawing_lines_corners_and_arcs_to_ascii() -> None:
    assert convert("│ ─ └── ═ ║", level=1) == "| - +-- = |"
    assert convert("╭─┬─╮\n│ │\n╰─┴─╯", level=1) == "+-+-+\n| |\n+-+-+"


def test_level_one_folds_geometric_triangles_circles_and_diamonds() -> None:
    assert convert("▲ △ ▴ ▵", level=1) == "^ ^ ^ ^"
    assert convert("▼ ▽ ▾ ▿", level=1) == "v v v v"
    assert convert("▶ ▷ ▸ ▹ ◀ ◁ ◂ ◃", level=1) == "> > > > < < < <"
    assert convert("● ○ ◉ ◎ ◯ ◆ ◇", level=1) == "o o o o o * *"


def test_level_zero_leaves_box_drawing_characters_alone() -> None:
    assert convert("│ ▼ ─ └ ▲") == "│ ▼ ─ └ ▲"


def test_level_two_preserves_diagram_structure_drawn_with_box_drawing_characters() -> (
    None
):
    diagram_text = (
        "   │  typed facades (chat, ...)\n"
        "   ▼\n"
        "Client / capability facades ── retries, result wrapping (boundary)\n"
        "   ▲\n"
        "   └── pure core: spec values -> encode/decode"
    )
    assert convert(diagram_text, level=2) == (
        "   |  typed facades (chat, ...)\n"
        "   v\n"
        "Client / capability facades -- retries, result wrapping (boundary)\n"
        "   ^\n"
        "   +-- pure core: spec values -> encode/decode"
    )


def test_level_two_drops_unmapped_non_ascii_characters_by_default() -> None:
    assert convert("Grüße aus München", level=2) == "Grusse aus Munchen"
    assert convert("日本語テキスト", level=2) == ""
    assert convert("π ≈ 3.14", level=2) == " ~ 3.14"


def test_level_two_replaces_unmapped_characters_when_a_replacement_is_given() -> None:
    assert convert("漢字!", level=2, replacement="?") == "??!"
    assert convert("a¶b", level=2, replacement="_") == "a_b"


def test_replacement_is_ignored_below_level_two() -> None:
    assert convert("日本語", level=0, replacement="?") == "日本語"
    assert convert("日本語", level=1, replacement="?") == "日本語"


def test_level_two_output_is_always_ascii_for_varied_inputs() -> None:
    samples = (
        "café ☕",
        "東京タワー",
        "Ελληνικά",
        "Привет мир",
        "𝕊𝕖𝕥 = {𝟙, 𝟚}",
        "e\u0301\u00a0—",
    )
    for sample in samples:
        for replacement in ("", "@"):
            converted_text = convert(sample, level=2, replacement=replacement)
            assert converted_text.isascii()


def test_level_two_matches_sequential_level_one_then_level_two_conversion() -> None:
    samples = ("café ☕ ½", "Ｈｅｌｌｏ — 日本", "ℕ ⊆ ℤ")
    for sample in samples:
        assert convert(convert(sample, level=1), level=2) == convert(sample, level=2)


def test_level_one_and_two_are_idempotent() -> None:
    samples = ("Crème brûlée — ½ €", "Ｈｅｌｌｏ ｗｏｒｌｄ", "“q” … café")
    for sample in samples:
        assert convert(convert(sample, level=1), level=1) == convert(sample, level=1)
        assert convert(convert(sample, level=2), level=2) == convert(sample, level=2)


def test_emoji_are_dropped_like_other_unmapped_text_by_default() -> None:
    assert convert("café 😀!", level=2) == "cafe !"
    assert convert("🇺🇸 日本", level=2) == " "


def test_keep_emoji_preserves_emoji_runs_verbatim() -> None:
    mixed_text = "café 😀! 🇺🇸 👨‍👩‍👧‍👦 ❤️ 👋🏽"
    assert convert(mixed_text, level=2, keep_emoji=True) == (
        "cafe 😀! 🇺🇸 👨‍👩‍👧‍👦 ❤️ 👋🏽"
    )
    assert convert(mixed_text, level=0, keep_emoji=True) == mixed_text


def test_explicitly_mapped_emoji_lookalikes_are_converted_not_kept() -> None:
    assert convert("➡", level=1, keep_emoji=True) == "->"
    assert convert("➖", level=0, keep_emoji=True) == "-"
    assert convert("➡😀", level=1, keep_emoji=True) == "->😀"
    assert convert("▶", level=1, keep_emoji=True) == ">"
    assert convert("◀😀", level=1, keep_emoji=True) == "<😀"


def test_mapped_characters_inside_an_emoji_run_are_kept_verbatim() -> None:
    assert convert("😀➡😀", level=1, keep_emoji=True) == "😀➡😀"


def test_convert_accepts_custom_conversion_tables() -> None:
    custom_tables = ConversionTables(
        normalization_table={0x2019: "'"},
        folding_table={0x00E9: "e"},
        emoji_run_pattern=EMOJI_RUN_PATTERN,
    )
    assert convert("it’s café", conversion_tables=custom_tables) == "it's café"
    assert convert("it’s café", conversion_tables=custom_tables, level=1) == "it's cafe"


def test_default_conversion_tables_wire_the_standard_tables() -> None:
    assert DEFAULT_CONVERSION_TABLES.normalization_table is NORMALIZATION_TABLE
    assert DEFAULT_CONVERSION_TABLES.folding_table is FOLDING_TABLE
    assert DEFAULT_CONVERSION_TABLES.emoji_run_pattern is EMOJI_RUN_PATTERN


def test_to_ascii_delegates_to_convert_with_the_same_arguments() -> None:
    conversion_argument_sets: tuple[tuple[str, dict[str, Any]], ...] = (
        ("café", {}),
        ("ＡＢＣ", {"level": 0}),
        ("⅓ … ☕", {"level": 1}),
        ("東京 → 東京 😀", {"level": 2, "replacement": "?", "keep_emoji": True}),
    )
    for sample_text, conversion_arguments in conversion_argument_sets:
        assert to_ascii(sample_text, **conversion_arguments) == convert(
            sample_text, **conversion_arguments
        )
