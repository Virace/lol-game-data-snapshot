from __future__ import annotations

from pathlib import Path

from league_tools.formats import WAD

from .targets import output_path_for_lcu_path


def output_path_for_lcu_target(snapshot_root: Path, lcu_path: str) -> Path:
    return snapshot_root / output_path_for_lcu_path(lcu_path)


def extract_targets_from_wads(*, wad_paths: list[Path], targets: list[str], snapshot_root: Path) -> None:
    def output_path(path: str) -> Path:
        return output_path_for_lcu_target(snapshot_root, path)

    for wad_path in wad_paths:
        WAD(wad_path).extract(targets, output_path)

