from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import logging

from .targets import BOOTSTRAP_ENTRIES

LOGGER = logging.getLogger(__name__)


def _file_payload(output_root: Path, path: Path) -> dict[str, str | int]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(output_root).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def write_metadata(
    *,
    output_root: Path,
    region: str,
    platform: str,
    lcu_manifest_url: str,
    lcu_manifest_id: str,
    game_version: str,
    languages: list[str],
    configuration_id: str,
) -> None:
    global_root = output_root / "global"
    files = sorted(
        (_file_payload(output_root, path) for path in global_root.rglob("*.json")),
        key=lambda item: str(item["path"]),
    )
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "region": region,
        "platform": platform,
        "configurationId": configuration_id,
        "gameVersion": game_version,
        "lcuManifestId": lcu_manifest_id,
        "lcuManifestUrl": lcu_manifest_url,
        "languages": languages,
        "targets": [*BOOTSTRAP_ENTRIES, "champions/{id}.json"],
        "files": files,
    }
    (output_root / "metadata.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    LOGGER.info("Wrote metadata for %d JSON files", len(files))
