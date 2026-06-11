from __future__ import annotations

from pathlib import Path
import logging
import subprocess

LOGGER = logging.getLogger(__name__)


def build_download_command(
    *,
    manifest_cli: Path,
    manifest_url: str,
    pattern: str,
    output_dir: Path,
) -> list[str]:
    return [
        str(manifest_cli),
        manifest_url,
        "-p",
        pattern,
        "-o",
        str(output_dir),
        "-s",
    ]


def download_matching_files(
    *,
    manifest_cli: Path,
    manifest_url: str,
    pattern: str,
    output_dir: Path,
) -> None:
    command = build_download_command(
        manifest_cli=manifest_cli,
        manifest_url=manifest_url,
        pattern=pattern,
        output_dir=output_dir,
    )
    LOGGER.info("Running manifest download: pattern=%s output_dir=%s", pattern, output_dir)
    subprocess.run(command, check=True)
