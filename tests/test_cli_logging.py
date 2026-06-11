import logging
from pathlib import Path

from lol_game_data_snapshot import cli


def test_cli_logs_error_and_returns_nonzero(monkeypatch, caplog) -> None:
    def raise_error():
        raise RuntimeError("patchline unavailable")

    monkeypatch.setattr(cli, "fetch_patchlines", raise_error)

    with caplog.at_level(logging.ERROR):
        result = cli.main(
            [
                "update",
                "--region",
                "OC1",
                "--manifest-cli",
                "manifest-cli",
            ]
        )

    assert result == 1
    assert any("Snapshot update failed" in record.getMessage() for record in caplog.records)


def test_cli_uses_pre_resolved_manifest_without_fetching_patchlines(monkeypatch) -> None:
    captured = {}

    def fail_fetch_patchlines():
        raise AssertionError("patchlines should not be fetched")

    def fake_build_snapshot_from_manifest(config, selection):
        captured["config"] = config
        captured["selection"] = selection

    monkeypatch.setattr(cli, "fetch_patchlines", fail_fetch_patchlines)
    monkeypatch.setattr(cli, "build_snapshot_from_manifest", fake_build_snapshot_from_manifest)

    result = cli.main(
        [
            "update",
            "--region",
            "oc1",
            "--manifest-cli",
            "manifest-cli",
            "--lcu-manifest-url",
            "https://example.invalid/ABCDEF.manifest",
            "--lcu-manifest-id",
            "ABCDEF",
            "--game-version",
            "16.12",
            "--configuration-id",
            "OC1",
        ]
    )

    assert result == 0
    assert captured["config"].manifest_cli == Path("manifest-cli")
    assert captured["selection"].region == "OC1"
    assert captured["selection"].url == "https://example.invalid/ABCDEF.manifest"
    assert captured["selection"].manifest_id == "ABCDEF"
    assert captured["selection"].game_version == "16.12"
