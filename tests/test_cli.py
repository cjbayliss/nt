import errno
import subprocess
import sys
from importlib.metadata import version as installed_package_version
from io import StringIO
from pathlib import Path

import pytest

from t2a.cli import (
    ConversionRequest,
    build_argument_parser,
    convert_input_file,
    convert_stream_lines,
    main,
)


def level_zero_request() -> ConversionRequest:
    return ConversionRequest(level=0, replacement="", keep_emoji=False)


def test_conversion_request_holds_the_converted_settings() -> None:
    assert ConversionRequest(
        level=2, replacement="?", keep_emoji=True
    ) == ConversionRequest(level=2, replacement="?", keep_emoji=True)
    assert ConversionRequest(
        level=2, replacement="?", keep_emoji=True
    ) != ConversionRequest(level=2, replacement="?", keep_emoji=False)


def test_argument_parser_defaults_to_stdin_at_level_zero_without_replacement() -> None:
    arguments = build_argument_parser().parse_args([])
    assert arguments.files == []
    assert arguments.level == 0
    assert arguments.replacement == ""
    assert arguments.keep_emoji is False


def test_argument_parser_accepts_level_replacement_keep_emoji_and_files() -> None:
    arguments = build_argument_parser().parse_args(
        ["-l", "2", "--replace", "?", "--keep-emoji", "a.txt", "b.txt"]
    )
    assert arguments.files == ["a.txt", "b.txt"]
    assert arguments.level == 2
    assert arguments.replacement == "?"
    assert arguments.keep_emoji is True


def test_argument_parser_accepts_long_level_option_and_stdin_marker() -> None:
    arguments = build_argument_parser().parse_args(["--level", "1", "-", "x.txt"])
    assert arguments.level == 1
    assert arguments.files == ["-", "x.txt"]


def test_argument_parser_rejects_unknown_levels_with_system_exit() -> None:
    with pytest.raises(SystemExit) as raised_system_exit:
        build_argument_parser().parse_args(["-l", "3"])
    assert raised_system_exit.value.code == 2


def test_argument_parser_prints_the_version_and_exits(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as raised_system_exit:
        build_argument_parser().parse_args(["--version"])
    assert raised_system_exit.value.code == 0
    assert capsys.readouterr().out == f"t2a {installed_package_version('t2a')}\n"


def test_convert_stream_lines_writes_converted_lines_to_the_output_stream() -> None:
    output_stream = StringIO()
    convert_stream_lines(
        StringIO("“q” — café\nＡＢＣ\n"),
        output_stream,
        ConversionRequest(level=2, replacement="", keep_emoji=False),
    )
    assert output_stream.getvalue() == '"q" - cafe\nABC\n'


def test_convert_input_file_reads_stdin_for_the_dash_file_name() -> None:
    output_stream = StringIO()
    encountered_error = convert_input_file(
        "-", StringIO("Ｈｅｌｌｏ\n"), output_stream, level_zero_request()
    )
    assert encountered_error is None
    assert output_stream.getvalue() == "Hello\n"


def test_convert_input_file_converts_a_utf_8_file(tmp_path: Path) -> None:
    input_file = tmp_path / "input.txt"
    input_file.write_text("naïve — café\n", encoding="utf-8")
    output_stream = StringIO()
    encountered_error = convert_input_file(
        str(input_file),
        StringIO(),
        output_stream,
        ConversionRequest(level=1, replacement="", keep_emoji=False),
    )
    assert encountered_error is None
    assert output_stream.getvalue() == "naive - cafe\n"


def test_convert_input_file_replaces_undecodable_bytes_before_conversion(
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "latin1.txt"
    input_file.write_bytes(b"caf\xe9\n")
    output_stream = StringIO()
    encountered_error = convert_input_file(
        str(input_file),
        StringIO(),
        output_stream,
        ConversionRequest(level=2, replacement="", keep_emoji=False),
    )
    assert encountered_error is None
    assert output_stream.getvalue() == "caf\n"


def test_convert_input_file_returns_the_os_error_for_missing_files(
    tmp_path: Path,
) -> None:
    missing_file_name = str(tmp_path / "missing.txt")
    output_stream = StringIO()
    encountered_error = convert_input_file(
        missing_file_name, StringIO(), output_stream, level_zero_request()
    )
    assert isinstance(encountered_error, OSError)
    assert encountered_error.errno == errno.ENOENT
    assert output_stream.getvalue() == ""


def test_main_converts_stdin_and_returns_zero(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO("“q” — café\n"))
    exit_code = main(["-l", "2"])
    assert exit_code == 0
    assert capsys.readouterr().out == '"q" - cafe\n'


def test_main_converts_each_file_in_argument_order(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    first_file = tmp_path / "first.txt"
    first_file.write_text("𝐀𝐛𝐜\n", encoding="utf-8")
    second_file = tmp_path / "second.txt"
    second_file.write_text("½½\n", encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", StringIO("unused\n"))
    exit_code = main([str(first_file), str(second_file), "-l", "1"])
    assert exit_code == 0
    assert capsys.readouterr().out == "Abc\n1/21/2\n"


def test_main_mixes_stdin_and_files_in_argument_order(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "input.txt"
    input_file.write_text("from-file\n", encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", StringIO("from-stdin\n"))
    exit_code = main(["-", str(input_file)])
    assert exit_code == 0
    assert capsys.readouterr().out == "from-stdin\nfrom-file\n"


def test_main_converts_files_before_a_missing_one_and_then_stops(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO("unused\n"))
    present_file = tmp_path / "present.txt"
    present_file.write_text("ＯＫ\n", encoding="utf-8")
    missing_file = tmp_path / "missing.txt"
    exit_code = main([str(present_file), str(missing_file)])
    captured_output = capsys.readouterr()
    assert exit_code == 1
    assert captured_output.out == "OK\n"
    assert "missing.txt" in captured_output.err
    assert captured_output.err.startswith("t2a: ")


def test_main_version_exits_zero_without_converting_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", StringIO("ＵＮＵＳＥＤ\n"))
    with pytest.raises(SystemExit) as raised_system_exit:
        main(["--version"])
    assert raised_system_exit.value.code == 0
    assert capsys.readouterr().out == f"t2a {installed_package_version('t2a')}\n"


def test_module_entry_point_converts_stdin_in_a_real_process() -> None:
    completed_process = subprocess.run(
        [sys.executable, "-m", "t2a", "-l", "1", "--keep-emoji"],
        input="Café ☕ «ɣ»\n",
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed_process.stdout == "Cafe ☕ <<ɣ>>\n"
