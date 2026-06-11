import json
from pathlib import Path

from lol_game_data_snapshot.metadata import write_metadata


def test_write_metadata_records_json_files(tmp_path: Path) -> None:
    (tmp_path / "global/default/v1").mkdir(parents=True)
    (tmp_path / ".tmp").mkdir()
    (tmp_path / "global/default/v1/items.json").write_text("[]", encoding="utf-8")
    (tmp_path / ".tmp/description.json").write_text("{}", encoding="utf-8")

    write_metadata(
        output_root=tmp_path,
        region="OC1",
        platform="windows",
        lcu_manifest_url="https://example.invalid/lcu.manifest",
        lcu_manifest_id="lcu",
        game_version="16.12",
        languages=["default"],
        configuration_id="OC1",
    )

    payload = json.loads((tmp_path / "metadata.json").read_text(encoding="utf-8"))

    assert payload["region"] == "OC1"
    assert payload["platform"] == "windows"
    assert payload["configurationId"] == "OC1"
    assert payload["gameVersion"] == "16.12"
    assert payload["lcuManifestId"] == "lcu"
    assert "summoner-spells.json" in payload["targets"]
    assert "championperkstylemap.json" in payload["targets"]
    assert payload["files"][0]["path"] == "global/default/v1/items.json"
    assert payload["files"][0]["bytes"] == 2
    assert len(payload["files"]) == 1
