from __future__ import annotations

from pathlib import Path
from typing import Any
import json

LCU_PLUGIN_PATH = "Plugins/rcp-be-lol-game-data"


def load_description(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bundle_names_for_language(description: dict[str, Any], language: str) -> list[str]:
    riot_meta = description.get("riotMeta")
    if not isinstance(riot_meta, dict):
        raise ValueError("description.json missing riotMeta object")

    if language.lower() in {"default", "en_us"}:
        bundle_names = riot_meta.get("globalAssetBundles", [])
    else:
        per_locale = riot_meta.get("perLocaleAssetBundles", {})
        if not isinstance(per_locale, dict):
            raise ValueError("description.json perLocaleAssetBundles must be an object")
        bundle_names = per_locale.get(language)
        if bundle_names is None:
            lower_lookup = {str(key).lower(): value for key, value in per_locale.items()}
            bundle_names = lower_lookup.get(language.lower(), [])

    if not isinstance(bundle_names, list):
        raise ValueError(f"description.json bundle list for {language} must be an array")
    return [str(name).strip() for name in bundle_names if str(name).strip()]


def description_pattern() -> str:
    return f"{LCU_PLUGIN_PATH}/description.json"


def bundle_pattern(bundle_name: str) -> str:
    return f"{LCU_PLUGIN_PATH}/{bundle_name}"


def find_downloaded_file(download_root: Path, suffix: str) -> Path:
    normalized_suffix = suffix.replace("\\", "/").lower()
    matches = [
        path
        for path in download_root.rglob("*")
        if path.is_file() and path.as_posix().lower().endswith(normalized_suffix)
    ]
    if not matches:
        raise FileNotFoundError(f"downloaded file not found: {suffix}")
    if len(matches) > 1:
        matches.sort(key=lambda item: len(item.as_posix()))
    return matches[0]


def find_bundle_files(download_root: Path, bundle_names: list[str]) -> list[Path]:
    return [find_downloaded_file(download_root, bundle_pattern(name)) for name in bundle_names]
