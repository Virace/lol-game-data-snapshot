#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${GITHUB_WORKSPACE:-$(pwd)}"
export PYTHONPATH="${PROJECT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

"${PYTHON:-python3}" -m lol_game_data_snapshot.check_update \
  --region "${SNAPSHOT_REGION:-OC1}" \
  --metadata "${SNAPSHOT_METADATA_PATH:-metadata.json}"
