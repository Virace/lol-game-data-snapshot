from __future__ import annotations

from collections.abc import Iterable
from typing import Any

RCP_GLOBAL_PREFIX = "plugins/rcp-be-lol-game-data/global"
PLUGIN_PREFIX = "plugins/rcp-be-lol-game-data/"
BOOTSTRAP_ENTRIES = (
    "champion-summary.json",
    "maps.json",
    "items.json",
    "summoner-spells.json",
    "universes.json",
    "skinlines.json",
    "queues.json",
    "game-mode-mutators.json",
    "perks.json",
    "perkstyles.json",
    "objectives.json",
    "skins.json",
    "champion-rune-recommendations.json",
    "championperkstylemap.json",
)


def build_lcu_v1_path(language: str, entry: str) -> str:
    return f"{RCP_GLOBAL_PREFIX}/{language}/v1/{entry}"


def build_bootstrap_targets(language: str) -> list[str]:
    return [build_lcu_v1_path(language, entry) for entry in BOOTSTRAP_ENTRIES]


def build_champion_targets(language: str, champion_summary: Iterable[dict[str, Any]]) -> list[str]:
    targets: list[str] = []
    for item in champion_summary:
        champion_id = item.get("id")
        if champion_id in (-1, None):
            continue
        targets.append(build_lcu_v1_path(language, f"champions/{champion_id}.json"))
    return targets


def output_path_for_lcu_path(lcu_path: str) -> str:
    if not lcu_path.startswith(PLUGIN_PREFIX):
        raise ValueError(f"not an rcp-be-lol-game-data path: {lcu_path}")
    return lcu_path.removeprefix(PLUGIN_PREFIX)
