from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .config import parse_languages
from .manifest_resolver import (
    ManifestSelection,
    fetch_patchlines,
    manifest_id_from_url,
    resolve_lcu_manifest_url,
)
from .snapshot_builder import SnapshotBuildConfig, build_snapshot_from_manifest

LOGGER = logging.getLogger(__name__)


class _BelowErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR


def configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if root_logger.handlers:
        return

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(_BelowErrorFilter())
    stdout_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)

    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lol-game-data-snapshot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update = subparsers.add_parser("update", help="Generate the current LCU JSON snapshot.")
    update.add_argument("--region", default="OC1")
    update.add_argument("--languages", default="default,zh_CN")
    update.add_argument("--output", type=Path, default=Path("."))
    update.add_argument("--manifest-cli", type=Path, required=True)
    update.add_argument("--work-dir", type=Path, default=None)
    update.add_argument("--lcu-manifest-url", default="")
    update.add_argument("--lcu-manifest-id", default="")
    update.add_argument("--game-version", default="")
    update.add_argument("--configuration-id", default="")
    return parser


def resolve_selection_for_update(args: argparse.Namespace) -> ManifestSelection:
    if args.lcu_manifest_url:
        region = args.region.upper()
        return ManifestSelection(
            region=region,
            platform="windows",
            url=args.lcu_manifest_url,
            configuration_id=args.configuration_id or region,
            game_version=args.game_version,
            manifest_id=args.lcu_manifest_id or manifest_id_from_url(args.lcu_manifest_url),
        )

    LOGGER.info("Fetching Riot patchlines config")
    return resolve_lcu_manifest_url(fetch_patchlines(), region=args.region)


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "update":
        try:
            languages = parse_languages(args.languages)
            LOGGER.info(
                "Starting snapshot update: region=%s languages=%s output=%s manifest_cli=%s",
                args.region,
                ",".join(languages),
                args.output,
                args.manifest_cli,
            )
            selection = resolve_selection_for_update(args)
            LOGGER.info(
                "Resolved LCU manifest: region=%s platform=%s configuration=%s version=%s id=%s url=%s",
                selection.region,
                selection.platform,
                selection.configuration_id,
                selection.game_version or "(unknown)",
                selection.manifest_id,
                selection.url,
            )
            config = SnapshotBuildConfig(
                region=selection.region,
                languages=languages,
                output_root=args.output,
                manifest_cli=args.manifest_cli,
                work_root=args.work_dir,
            )
            build_snapshot_from_manifest(config, selection)
            LOGGER.info("Snapshot update completed")
            return 0
        except Exception:
            LOGGER.exception("Snapshot update failed")
            return 1
    return 0
