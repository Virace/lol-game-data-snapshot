from lol_game_data_snapshot import __version__
from lol_game_data_snapshot.cli import build_parser


def test_import_version() -> None:
    assert __version__ == "0.1.0"


def test_cli_update_arguments_parse() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "update",
            "--region",
            "OC1",
            "--languages",
            "default,zh_CN",
            "--manifest-cli",
            "bin/manifest-cli",
        ]
    )

    assert args.command == "update"
    assert args.region == "OC1"
    assert args.languages == "default,zh_CN"

