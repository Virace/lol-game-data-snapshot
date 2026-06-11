import json
from pathlib import Path

from lol_game_data_snapshot.check_update import check_snapshot_update, github_output_values


def _payload(*, version: str = "16.12", manifest_id: str = "NEWID") -> dict:
    return {
        "patchline": {
            "version": version,
            "platforms": {
                "win": {
                    "configurations": [
                        {
                            "id": "OC1",
                            "patch_url": f"https://example.invalid/{manifest_id}.manifest",
                        }
                    ]
                }
            },
        }
    }


def _write_metadata(
    path: Path,
    *,
    game_version: str = "16.12",
    lcu_manifest_id: str = "NEWID",
    lcu_manifest_url: str = "https://example.invalid/NEWID.manifest",
) -> None:
    path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "region": "OC1",
                "platform": "windows",
                "configurationId": "OC1",
                "gameVersion": game_version,
                "lcuManifestId": lcu_manifest_id,
                "lcuManifestUrl": lcu_manifest_url,
            }
        ),
        encoding="utf-8",
    )


def test_check_snapshot_update_updates_when_metadata_missing(tmp_path: Path) -> None:
    result = check_snapshot_update(_payload(), metadata_path=tmp_path / "metadata.json", region="OC1")

    assert result.should_update is True
    assert result.reason == "metadata-missing"
    assert result.selection.url == "https://example.invalid/NEWID.manifest"


def test_check_snapshot_update_skips_when_manifest_metadata_matches(tmp_path: Path) -> None:
    metadata_path = tmp_path / "metadata.json"
    _write_metadata(metadata_path)

    result = check_snapshot_update(_payload(), metadata_path=metadata_path, region="OC1")

    assert result.should_update is False
    assert result.reason == "snapshot-current"


def test_check_snapshot_update_updates_when_same_version_has_different_manifest_id(
    tmp_path: Path,
) -> None:
    metadata_path = tmp_path / "metadata.json"
    _write_metadata(
        metadata_path,
        game_version="16.12",
        lcu_manifest_id="OLDID",
        lcu_manifest_url="https://example.invalid/OLDID.manifest",
    )

    result = check_snapshot_update(
        _payload(version="16.12", manifest_id="NEWID"),
        metadata_path=metadata_path,
        region="OC1",
    )

    assert result.should_update is True
    assert result.reason == "lcu-manifest-id-changed"


def test_check_snapshot_update_can_force_manual_update(tmp_path: Path) -> None:
    metadata_path = tmp_path / "metadata.json"
    _write_metadata(metadata_path)

    result = check_snapshot_update(
        _payload(),
        metadata_path=metadata_path,
        region="OC1",
        force=True,
    )

    assert result.should_update is True
    assert result.reason == "manual-force"
    assert github_output_values(result)["should_update"] == "true"
