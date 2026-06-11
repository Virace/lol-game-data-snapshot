from lol_game_data_snapshot.config import parse_languages
from lol_game_data_snapshot.targets import (
    build_bootstrap_targets,
    build_champion_targets,
    build_lcu_v1_path,
    output_path_for_lcu_path,
)


def test_parse_languages_keeps_order_and_default() -> None:
    assert parse_languages("default,zh_CN") == ["default", "zh_CN"]


def test_parse_languages_inserts_default_when_missing() -> None:
    assert parse_languages("zh_CN") == ["default", "zh_CN"]


def test_build_bootstrap_targets_includes_all_top_level_json() -> None:
    assert build_bootstrap_targets("default") == [
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
    ]


def test_build_champion_targets_skips_negative_id() -> None:
    summary = [{"id": -1}, {"id": 1}, {"id": 2}]

    assert build_champion_targets("zh_CN", summary) == [
        "plugins/rcp-be-lol-game-data/global/zh_CN/v1/champions/1.json",
        "plugins/rcp-be-lol-game-data/global/zh_CN/v1/champions/2.json",
    ]


def test_build_lcu_v1_path() -> None:
    assert (
        build_lcu_v1_path("zh_CN", "items.json")
        == "plugins/rcp-be-lol-game-data/global/zh_CN/v1/items.json"
    )


def test_output_path_for_lcu_path_removes_plugin_prefix() -> None:
    assert (
        output_path_for_lcu_path("plugins/rcp-be-lol-game-data/global/default/v1/items.json")
        == "global/default/v1/items.json"
    )
