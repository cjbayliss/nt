from types import MappingProxyType

from nt.tables import (
    ENCLOSED_NEGATIVE_LETTER_RUN_STARTS,
    EXPLICITLY_MAPPED_CODEPOINTS,
    FOLDING_TABLE,
    FULLWIDTH_DIGIT_RUN_START,
    FULLWIDTH_LOWERCASE_LETTER_RUN_START,
    FULLWIDTH_UPPERCASE_LETTER_RUN_START,
    MATHEMATICAL_DIGIT_RUN_START,
    NORMALIZATION_TABLE,
    enclosed_negative_letter_replacements,
    enclosed_number_replacements,
    fullwidth_alphanumeric_replacements,
    mathematical_digit_replacements,
    mathematical_letter_replacements,
    replacements_keyed_by_codepoint,
    unicode_space_replacements,
)


def test_replacements_keyed_by_codepoint_maps_character_ordinals_to_replacements() -> (
    None
):
    assert replacements_keyed_by_codepoint({"…": "...", "’": "'"}) == {
        0x2026: "...",
        0x2019: "'",
    }


def test_mathematical_letter_replacements_cover_uppercase_and_lowercase_per_run() -> (
    None
):
    replacements = mathematical_letter_replacements((0x1D400, 0x1D538))
    assert len(replacements) == 104
    assert replacements[0x1D400] == "A"
    assert replacements[0x1D419] == "Z"
    assert replacements[0x1D41A] == "a"
    assert replacements[0x1D433] == "z"
    assert replacements[0x1D538] == "A"


def test_mathematical_digit_replacements_cover_five_consecutive_runs() -> None:
    replacements = mathematical_digit_replacements(MATHEMATICAL_DIGIT_RUN_START)
    assert len(replacements) == 50
    assert replacements[0x1D7CE] == "0"
    assert replacements[0x1D7D7] == "9"
    assert replacements[0x1D7D8] == "0"
    assert replacements[0x1D7E1] == "9"
    assert replacements[0x1D7F6] == "0"
    assert replacements[0x1D7FF] == "9"


def test_enclosed_negative_letter_replacements_map_to_ascii_letters() -> None:
    replacements = enclosed_negative_letter_replacements(
        ENCLOSED_NEGATIVE_LETTER_RUN_STARTS
    )
    assert len(replacements) == 52
    assert replacements[0x1F150] == "A"
    assert replacements[0x1F169] == "Z"
    assert replacements[0x1F170] == "A"
    assert replacements[0x1F189] == "Z"


def test_fullwidth_alphanumeric_replacements_map_to_ascii() -> None:
    replacements = fullwidth_alphanumeric_replacements(
        FULLWIDTH_DIGIT_RUN_START,
        FULLWIDTH_UPPERCASE_LETTER_RUN_START,
        FULLWIDTH_LOWERCASE_LETTER_RUN_START,
    )
    assert len(replacements) == 62
    assert replacements[0xFF10] == "0"
    assert replacements[0xFF19] == "9"
    assert replacements[0xFF21] == "A"
    assert replacements[0xFF3A] == "Z"
    assert replacements[0xFF41] == "a"
    assert replacements[0xFF5A] == "z"


def test_unicode_space_replacements_map_every_codepoint_to_a_space() -> None:
    assert unicode_space_replacements((0x00A0, 0x2000, 0x3000)) == {
        0x00A0: " ",
        0x2000: " ",
        0x3000: " ",
    }


def test_enclosed_number_replacements_map_circled_numbers_to_digit_strings() -> None:
    replacements = enclosed_number_replacements(0x2776, 0x24EB)
    assert replacements[0x2776] == "1"
    assert replacements[0x277F] == "10"
    assert replacements[0x24EB] == "11"
    assert replacements[0x24F4] == "20"


def test_every_normalization_and_folding_replacement_is_ascii() -> None:
    assert all(value.isascii() for value in NORMALIZATION_TABLE.values())
    assert all(value.isascii() for value in FOLDING_TABLE.values())


def test_every_table_key_is_a_non_ascii_codepoint() -> None:
    assert all(codepoint > 0x7F for codepoint in NORMALIZATION_TABLE)
    assert all(codepoint > 0x7F for codepoint in FOLDING_TABLE)


def test_normalization_table_contains_the_documented_presentational_mappings() -> None:
    assert NORMALIZATION_TABLE[0x2019] == "'"
    assert NORMALIZATION_TABLE[0x201C] == '"'
    assert NORMALIZATION_TABLE[0x2014] == "-"
    assert NORMALIZATION_TABLE[0x2026] == "..."
    assert NORMALIZATION_TABLE[0x2102] == "C"
    assert NORMALIZATION_TABLE[0x1D400] == "A"
    assert NORMALIZATION_TABLE[0xFF21] == "A"
    assert NORMALIZATION_TABLE[0x00A0] == " "
    assert NORMALIZATION_TABLE[0x00AD] == ""


def test_folding_table_contains_the_documented_folding_mappings() -> None:
    assert FOLDING_TABLE[0x00DF] == "ss"
    assert FOLDING_TABLE[0x0153] == "oe"
    assert FOLDING_TABLE[0x2044] == "/"
    assert FOLDING_TABLE[0x00A9] == "(c)"
    assert FOLDING_TABLE[0x20AC] == "EUR"
    assert FOLDING_TABLE[0x2192] == "->"
    assert FOLDING_TABLE[0x2776] == "1"


def test_normalization_and_folding_tables_are_read_only_proxies() -> None:
    assert isinstance(NORMALIZATION_TABLE, MappingProxyType)
    assert isinstance(FOLDING_TABLE, MappingProxyType)


def test_explicitly_mapped_codepoints_unite_both_tables() -> None:
    assert (
        frozenset(NORMALIZATION_TABLE) | frozenset(FOLDING_TABLE)
        == EXPLICITLY_MAPPED_CODEPOINTS
    )
    assert 0x2019 in EXPLICITLY_MAPPED_CODEPOINTS
    assert 0x27A1 in EXPLICITLY_MAPPED_CODEPOINTS
    assert 0x1F600 not in EXPLICITLY_MAPPED_CODEPOINTS
