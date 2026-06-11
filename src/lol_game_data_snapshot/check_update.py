from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import argparse
import json
import logging
import os

from .manifest_resolver import ManifestSelection, fetch_patchlines, resolve_lcu_manifest_url

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SnapshotUpdateCheck:
    selection: ManifestSelection
    should_update: bool
    reason: str


def _read_metadata(metadata_path: Path) -> dict[str, Any] | None:
    if not metadata_path.exists():
        return None
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"metadata must be a JSON object: {metadata_path}")
    return payload


def check_snapshot_update(
    payload: dict[str, Any],
    *,
    metadata_path: Path,
    region: str,
    force: bool = False,
) -> SnapshotUpdateCheck:
    selection = resolve_lcu_manifest_url(payload, region=region)
    if force:
        return SnapshotUpdateCheck(selection=selection, should_update=True, reason="manual-force")

    metadata = _read_metadata(metadata_path)
    if metadata is None:
        return SnapshotUpdateCheck(selection=selection, should_update=True, reason="metadata-missing")

    comparisons = [
        ("region", metadata.get("region"), selection.region, "region-changed"),
        ("platform", metadata.get("platform"), selection.platform, "platform-changed"),
        (
            "configurationId",
            metadata.get("configurationId"),
            selection.configuration_id,
            "configuration-id-changed",
        ),
    ]
    for _field_name, previous, current, reason in comparisons:
        if str(previous or "") != str(current or ""):
            return SnapshotUpdateCheck(selection=selection, should_update=True, reason=reason)

    if selection.game_version and str(metadata.get("gameVersion") or "") != selection.game_version:
        return SnapshotUpdateCheck(
            selection=selection,
            should_update=True,
            reason="game-version-changed",
        )

    if str(metadata.get("lcuManifestId") or "") != selection.manifest_id:
        return SnapshotUpdateCheck(
            selection=selection,
            should_update=True,
            reason="lcu-manifest-id-changed",
        )

    if str(metadata.get("lcuManifestUrl") or "") != selection.url:
        return SnapshotUpdateCheck(
            selection=selection,
            should_update=True,
            reason="lcu-manifest-url-changed",
        )

    return SnapshotUpdateCheck(selection=selection, should_update=False, reason="snapshot-current")


def github_output_values(result: SnapshotUpdateCheck) -> dict[str, str]:
    selection = result.selection
    return {
        "should_update": "true" if result.should_update else "false",
        "reason": result.reason,
        "region": selection.region,
        "platform": selection.platform,
        "configuration_id": selection.configuration_id,
        "manifest_url": selection.url,
        "game_version": selection.game_version,
        "lcu_manifest_id": selection.manifest_id,
    }


def write_github_outputs(result: SnapshotUpdateCheck, output_path: Path) -> None:
    values = github_output_values(result)
    with output_path.open("a", encoding="utf-8", newline="\n") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m lol_game_data_snapshot.check_update",
        description="Resolve the current LCU manifest and compare it with local metadata.",
    )
    parser.add_argument("--region", default=os.environ.get("SNAPSHOT_REGION", "OC1"))
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path(os.environ.get("SNAPSHOT_METADATA_PATH", "metadata.json")),
    )
    parser.add_argument("--patchlines-json", type=Path, default=None)
    parser.add_argument("--github-output", type=Path, default=None)
    parser.add_argument(
        "--force",
        action="store_true",
        default=os.environ.get("SNAPSHOT_FORCE_UPDATE", "").lower() == "true",
        help="Force an update even when local metadata matches the current manifest.",
    )
    return parser


def _load_patchlines(path: Path | None) -> dict[str, Any]:
    if path is None:
        LOGGER.info("Fetching Riot patchlines config")
        return fetch_patchlines()
    LOGGER.info("Loading Riot patchlines config from %s", path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"patchlines payload must be a JSON object: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = check_snapshot_update(
            _load_patchlines(args.patchlines_json),
            metadata_path=args.metadata,
            region=args.region,
            force=args.force,
        )
        selection = result.selection
        LOGGER.info(
            "Resolved LCU manifest: region=%s platform=%s configuration=%s version=%s id=%s url=%s",
            selection.region,
            selection.platform,
            selection.configuration_id,
            selection.game_version or "(unknown)",
            selection.manifest_id,
            selection.url,
        )
        LOGGER.info(
            "Snapshot update check: should_update=%s reason=%s metadata=%s",
            result.should_update,
            result.reason,
            args.metadata,
        )

        github_output = args.github_output or os.environ.get("GITHUB_OUTPUT")
        if github_output:
            write_github_outputs(result, Path(github_output))
        else:
            for key, value in github_output_values(result).items():
                print(f"{key}={value}")
        return 0
    except Exception:
        LOGGER.exception("Snapshot update check failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
