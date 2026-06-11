from lol_game_data_snapshot.manifest_resolver import (
    manifest_id_from_url,
    resolve_lcu_manifest_url,
)


def test_resolve_lcu_manifest_url_for_region_and_windows() -> None:
    payload = {
        "patchline": {
            "version": "16.12",
            "platforms": {
                "win": {
                    "configurations": [
                        {"id": "NA1", "patch_url": "https://example.invalid/na.manifest"},
                        {
                            "id": "OC1",
                            "patch_url": (
                                "https://lol.secure.dyn.riotcdn.net/channels/public/releases/"
                                "CF5227813B5D0807.manifest"
                            ),
                        },
                    ]
                },
                "mac": {
                    "configurations": [
                        {"id": "OC1", "patch_url": "https://example.invalid/mac.manifest"}
                    ]
                },
            }
        }
    }

    result = resolve_lcu_manifest_url(payload, region="OC1")

    assert result.region == "OC1"
    assert result.platform == "windows"
    assert result.url == (
        "https://lol.secure.dyn.riotcdn.net/channels/public/releases/"
        "CF5227813B5D0807.manifest"
    )
    assert result.configuration_id == "OC1"
    assert result.game_version == "16.12"
    assert result.manifest_id == "CF5227813B5D0807"


def test_resolve_lcu_manifest_url_falls_back_to_theme_manifest_version() -> None:
    payload = {
        "patchline": {
            "version": "",
            "platforms": {
                "win": {
                    "configurations": [
                        {
                            "id": "OC1",
                            "patch_url": "https://example.invalid/ABCDEF.manifest",
                            "metadata": {
                                "theme_manifest": (
                                    "https://lol.secure.dyn.riotcdn.net/channels/public/"
                                    "rccontent/theme/16.13/OC1/manifest.json"
                                )
                            },
                        },
                    ]
                },
            },
        }
    }

    result = resolve_lcu_manifest_url(payload, region="oc1")

    assert result.game_version == "16.13"


def test_manifest_id_from_url_uses_manifest_file_stem() -> None:
    assert manifest_id_from_url(
        "https://lol.secure.dyn.riotcdn.net/channels/public/releases/CF5227813B5D0807.manifest"
    ) == "CF5227813B5D0807"


def test_resolve_lcu_manifest_url_raises_for_missing_region() -> None:
    payload = {"patchline": {"platforms": {"win": {"configurations": []}}}}

    try:
        resolve_lcu_manifest_url(payload, region="OC1")
    except LookupError as exc:
        assert "OC1" in str(exc)
    else:
        raise AssertionError("expected LookupError")
