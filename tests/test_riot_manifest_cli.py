from pathlib import Path

from lol_game_data_snapshot.riot_manifest_cli import build_download_command


def test_build_download_command_uses_manifest_cli() -> None:
    command = build_download_command(
        manifest_cli=Path("bin/manifest-cli.exe"),
        manifest_url="https://example.invalid/lcu.manifest",
        pattern="Plugins/rcp-be-lol-game-data/description.json",
        output_dir=Path("work/downloads"),
    )

    assert command == [
        str(Path("bin/manifest-cli.exe")),
        "https://example.invalid/lcu.manifest",
        "-p",
        "Plugins/rcp-be-lol-game-data/description.json",
        "-o",
        str(Path("work/downloads")),
        "-s",
    ]
