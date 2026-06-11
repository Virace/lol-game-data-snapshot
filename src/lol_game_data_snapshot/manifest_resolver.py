from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import json
import re

THEME_VERSION_PATTERN = re.compile(r"/theme/([^/]+)/", re.IGNORECASE)

PATCHLINES_URL = (
    "https://clientconfig.rpg.riotgames.com/api/v1/config/public"
    "?namespace=keystone.products.league_of_legends.patchlines"
)


@dataclass(frozen=True)
class ManifestSelection:
    region: str
    platform: str
    url: str
    configuration_id: str
    game_version: str = ""
    manifest_id: str = ""


def fetch_patchlines() -> dict[str, Any]:
    request = Request(PATCHLINES_URL, headers={"User-Agent": "lol-game-data-snapshot/0.1"})
    with urlopen(request, timeout=20) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def manifest_id_from_url(url: str) -> str:
    name = urlsplit(url).path.rsplit("/", maxsplit=1)[-1]
    if name.endswith(".manifest"):
        return name[: -len(".manifest")]
    return name


def game_version_from_patchline(
    patchline: dict[str, Any],
    configuration: dict[str, Any],
) -> str:
    version = str(patchline.get("version", "")).strip()
    if version:
        return version

    metadata = configuration.get("metadata", {})
    if not isinstance(metadata, dict):
        return ""
    theme_manifest = str(metadata.get("theme_manifest", "")).strip()
    match = THEME_VERSION_PATTERN.search(theme_manifest)
    if match:
        return match.group(1)
    return ""


def resolve_lcu_manifest_url(payload: dict[str, Any], *, region: str) -> ManifestSelection:
    normalized_region = region.upper()
    for patchline in payload.values():
        if not isinstance(patchline, dict):
            continue
        platforms = patchline.get("platforms", {})
        if not isinstance(platforms, dict):
            continue
        windows = platforms.get("win") or platforms.get("windows")
        if not isinstance(windows, dict):
            continue
        for configuration in windows.get("configurations", []):
            if not isinstance(configuration, dict):
                continue
            configuration_id = str(configuration.get("id", "")).upper()
            if configuration_id != normalized_region:
                continue
            patch_url = str(configuration.get("patch_url", "")).strip()
            if patch_url:
                return ManifestSelection(
                    region=normalized_region,
                    platform="windows",
                    url=patch_url,
                    configuration_id=str(configuration.get("id", "")),
                    game_version=game_version_from_patchline(patchline, configuration),
                    manifest_id=manifest_id_from_url(patch_url),
                )
    raise LookupError(f"unable to resolve Windows LCU manifest for region {normalized_region}")
