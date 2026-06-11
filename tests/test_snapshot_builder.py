import json
import logging
from pathlib import Path

from lol_game_data_snapshot.manifest_resolver import ManifestSelection
from lol_game_data_snapshot import snapshot_builder
from lol_game_data_snapshot.snapshot_builder import SnapshotBuildConfig, build_snapshot


def test_build_snapshot_extracts_items_and_derived_champions(tmp_path: Path) -> None:
    output = tmp_path / "snapshot"
    calls: list[tuple[str, list[str]]] = []

    def fake_extract(language: str, targets: list[str]) -> None:
        calls.append((language, targets))
        base = output / "global" / language / "v1"
        base.mkdir(parents=True, exist_ok=True)
        if any(target.endswith("champion-summary.json") for target in targets):
            (base / "champion-summary.json").write_text(
                json.dumps([{"id": 1}, {"id": -1}], ensure_ascii=False),
                encoding="utf-8",
            )
            (base / "maps.json").write_text("[]", encoding="utf-8")
            (base / "items.json").write_text("[]", encoding="utf-8")
        if any(target.endswith("champions/1.json") for target in targets):
            champions = base / "champions"
            champions.mkdir(parents=True, exist_ok=True)
            (champions / "1.json").write_text("{}", encoding="utf-8")

    config = SnapshotBuildConfig(region="OC1", languages=["default"], output_root=output)

    build_snapshot(config, extract_language_targets=fake_extract)

    assert (output / "global/default/v1/items.json").exists()
    assert (output / "global/default/v1/champions/1.json").exists()
    assert calls == [
        (
            "default",
            [
                "plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/maps.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/items.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/universes.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/skinlines.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/queues.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/game-mode-mutators.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/perks.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/perkstyles.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/objectives.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/skins.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/champion-rune-recommendations.json",
                "plugins/rcp-be-lol-game-data/global/default/v1/championperkstylemap.json",
            ],
        ),
        (
            "default",
            ["plugins/rcp-be-lol-game-data/global/default/v1/champions/1.json"],
        ),
    ]


def test_build_snapshot_from_manifest_downloads_language_bundles_once(
    tmp_path: Path, monkeypatch
) -> None:
    output = tmp_path / "snapshot"
    work_root = tmp_path / "work"
    calls: list[str] = []

    def fake_download_matching_files(*, pattern: str, output_dir: Path, **_kwargs) -> None:
        calls.append(pattern)
        if pattern.endswith("description.json"):
            target = output_dir / "Plugins/rcp-be-lol-game-data/description.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(
                    {
                        "riotMeta": {
                            "globalAssetBundles": ["default-assets.wad"],
                            "perLocaleAssetBundles": {},
                        }
                    }
                ),
                encoding="utf-8",
            )
        elif pattern.endswith("default-assets.wad"):
            target = output_dir / "Plugins/rcp-be-lol-game-data/default-assets.wad"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"wad")

    def fake_extract_targets_from_wads(
        *, targets: list[str], snapshot_root: Path, **_kwargs
    ) -> None:
        base = snapshot_root / "global/default/v1"
        base.mkdir(parents=True, exist_ok=True)
        if any(target.endswith("champion-summary.json") for target in targets):
            (base / "champion-summary.json").write_text(
                json.dumps([{"id": 1}], ensure_ascii=False),
                encoding="utf-8",
            )
        if any(target.endswith("champions/1.json") for target in targets):
            champions = base / "champions"
            champions.mkdir(exist_ok=True)
            (champions / "1.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(snapshot_builder, "download_matching_files", fake_download_matching_files)
    monkeypatch.setattr(snapshot_builder, "extract_targets_from_wads", fake_extract_targets_from_wads)

    snapshot_builder.build_snapshot_from_manifest(
        SnapshotBuildConfig(
            region="OC1",
            languages=["default"],
            output_root=output,
            manifest_cli=Path("manifest-cli"),
            work_root=work_root,
        ),
        ManifestSelection(
            region="OC1",
            platform="windows",
            url="https://example.invalid/lcu.manifest",
            configuration_id="OC1",
        ),
    )

    assert calls.count("Plugins/rcp-be-lol-game-data/default-assets.wad") == 1


def test_build_snapshot_from_manifest_logs_key_stages(
    tmp_path: Path, monkeypatch, caplog
) -> None:
    output = tmp_path / "snapshot"
    work_root = tmp_path / "work"

    def fake_download_matching_files(*, pattern: str, output_dir: Path, **_kwargs) -> None:
        if pattern.endswith("description.json"):
            target = output_dir / "Plugins/rcp-be-lol-game-data/description.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(
                    {
                        "riotMeta": {
                            "globalAssetBundles": ["default-assets.wad"],
                            "perLocaleAssetBundles": {},
                        }
                    }
                ),
                encoding="utf-8",
            )
        elif pattern.endswith("default-assets.wad"):
            target = output_dir / "Plugins/rcp-be-lol-game-data/default-assets.wad"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"wad")

    def fake_extract_targets_from_wads(*, targets: list[str], snapshot_root: Path, **_kwargs) -> None:
        base = snapshot_root / "global/default/v1"
        base.mkdir(parents=True, exist_ok=True)
        if any(target.endswith("champion-summary.json") for target in targets):
            (base / "champion-summary.json").write_text(
                json.dumps([{"id": 1}], ensure_ascii=False),
                encoding="utf-8",
            )
        if any(target.endswith("champions/1.json") for target in targets):
            champions = base / "champions"
            champions.mkdir(exist_ok=True)
            (champions / "1.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(snapshot_builder, "download_matching_files", fake_download_matching_files)
    monkeypatch.setattr(snapshot_builder, "extract_targets_from_wads", fake_extract_targets_from_wads)

    with caplog.at_level(logging.INFO):
        snapshot_builder.build_snapshot_from_manifest(
            SnapshotBuildConfig(
                region="OC1",
                languages=["default"],
                output_root=output,
                manifest_cli=Path("manifest-cli"),
                work_root=work_root,
            ),
            ManifestSelection(
                region="OC1",
                platform="windows",
                url="https://example.invalid/lcu.manifest",
                configuration_id="OC1",
            ),
        )

    messages = [record.getMessage() for record in caplog.records]
    assert any("Downloading LCU description" in message for message in messages)
    assert any("Resolved LCU bundles for language default" in message for message in messages)
    assert any("Extracting 14 bootstrap targets for language default" in message for message in messages)
    assert any("Extracting 1 champion detail targets for language default" in message for message in messages)
    assert any("Snapshot metadata written" in message for message in messages)
