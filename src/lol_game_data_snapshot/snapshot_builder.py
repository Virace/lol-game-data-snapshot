from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import shutil

from .lcu_resources import (
    bundle_names_for_language,
    bundle_pattern,
    description_pattern,
    find_bundle_files,
    find_downloaded_file,
    load_description,
)
from .manifest_resolver import ManifestSelection, manifest_id_from_url
from .metadata import write_metadata
from .riot_manifest_cli import download_matching_files
from .targets import build_bootstrap_targets, build_champion_targets
from .wad_extract import extract_targets_from_wads

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SnapshotBuildConfig:
    region: str
    languages: list[str]
    output_root: Path
    manifest_cli: Path | None = None
    work_root: Path | None = None


def load_champion_summary(output_root: Path, language: str) -> list[dict]:
    path = output_root / "global" / language / "v1" / "champion-summary.json"
    if not path.exists():
        raise FileNotFoundError(f"champion summary was not extracted: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"champion summary must be a JSON array: {path}")
    return payload


def build_snapshot(
    config: SnapshotBuildConfig,
    *,
    extract_language_targets: Callable[[str, list[str]], None],
) -> None:
    for language in config.languages:
        bootstrap_targets = build_bootstrap_targets(language)
        LOGGER.info(
            "Extracting %d bootstrap targets for language %s",
            len(bootstrap_targets),
            language,
        )
        extract_language_targets(language, bootstrap_targets)

        champion_summary = load_champion_summary(config.output_root, language)
        champion_targets = build_champion_targets(language, champion_summary)
        LOGGER.info(
            "Extracting %d champion detail targets for language %s",
            len(champion_targets),
            language,
        )
        extract_language_targets(language, champion_targets)


def clean_generated_output(output_root: Path) -> None:
    global_root = output_root / "global"
    if global_root.exists():
        LOGGER.info("Removing existing generated output: %s", global_root)
        shutil.rmtree(global_root)
    metadata_path = output_root / "metadata.json"
    if metadata_path.exists():
        LOGGER.info("Removing existing metadata: %s", metadata_path)
        metadata_path.unlink()


def build_snapshot_from_manifest(config: SnapshotBuildConfig, selection: ManifestSelection) -> None:
    if config.manifest_cli is None:
        raise ValueError("manifest_cli is required for live snapshot generation")

    output_root = config.output_root
    work_root = config.work_root or output_root / ".tmp" / "snapshot-work"
    download_root = work_root / "downloads"
    LOGGER.info(
        "Building snapshot from manifest: region=%s platform=%s languages=%s",
        selection.region,
        selection.platform,
        ",".join(config.languages),
    )
    LOGGER.info("Using work directory: %s", work_root)
    download_root.mkdir(parents=True, exist_ok=True)
    clean_generated_output(output_root)

    LOGGER.info("Downloading LCU description: pattern=%s", description_pattern())
    download_matching_files(
        manifest_cli=config.manifest_cli,
        manifest_url=selection.url,
        pattern=description_pattern(),
        output_dir=download_root,
    )
    description_path = find_downloaded_file(download_root, description_pattern())
    LOGGER.info("Loaded LCU description: %s", description_path)
    description = load_description(description_path)
    language_wad_cache: dict[str, list[Path]] = {}

    def wad_paths_for_language(language: str) -> list[Path]:
        cached_paths = language_wad_cache.get(language)
        if cached_paths is not None:
            return cached_paths

        bundle_names = bundle_names_for_language(description, language)
        if not bundle_names:
            raise LookupError(f"no LCU asset bundles found for language {language}")
        LOGGER.info(
            "Resolved LCU bundles for language %s: %s",
            language,
            ", ".join(bundle_names),
        )
        for bundle_name in bundle_names:
            pattern = bundle_pattern(bundle_name)
            try:
                cached_path = find_downloaded_file(download_root, pattern)
                LOGGER.info("Reusing cached LCU bundle: language=%s path=%s", language, cached_path)
            except FileNotFoundError:
                LOGGER.info("Downloading LCU bundle: language=%s pattern=%s", language, pattern)
                download_matching_files(
                    manifest_cli=config.manifest_cli,
                    manifest_url=selection.url,
                    pattern=pattern,
                    output_dir=download_root,
                )
        wad_paths = find_bundle_files(download_root, bundle_names)
        LOGGER.info("Resolved %d local WAD files for language %s", len(wad_paths), language)
        language_wad_cache[language] = wad_paths
        return wad_paths

    def extract_language_targets(language: str, targets: list[str]) -> None:
        wad_paths = wad_paths_for_language(language)
        LOGGER.info(
            "Extracting targets from WADs: language=%s target_count=%d wad_count=%d",
            language,
            len(targets),
            len(wad_paths),
        )
        extract_targets_from_wads(wad_paths=wad_paths, targets=targets, snapshot_root=output_root)

    build_snapshot(config, extract_language_targets=extract_language_targets)
    write_metadata(
        output_root=output_root,
        region=selection.region,
        platform=selection.platform,
        lcu_manifest_url=selection.url,
        lcu_manifest_id=selection.manifest_id or manifest_id_from_url(selection.url),
        game_version=selection.game_version,
        languages=config.languages,
        configuration_id=selection.configuration_id,
    )
    metadata_path = output_root / "metadata.json"
    LOGGER.info("Snapshot metadata written: %s", metadata_path)
