#!/usr/bin/env bash
set -euo pipefail

rclone version

if [[ ! -f /config/rclone.conf ]]; then
  echo "[ERROR] Missing file /config/rclone.conf" >&2
  exit 1
fi
if [[ ! -f /config/jobs.json ]]; then
  echo "[ERROR] Missing file /config/jobs.json" >&2
  exit 1
fi

# Struktura: { "jobs": [ {"source": "remote:/path", "destination": "remote2:/path"}, ... ] }

TOTAL=$(jq '.jobs | length' /config/jobs.json)
echo "[INFO] Jobs count: ${TOTAL}"

idx=0
jq -c '.jobs[]' /config/jobs.json | while read -r job; do
  idx=$((idx+1))
  src=$(echo "$job" | jq -r '.source')
  dst=$(echo "$job" | jq -r '.destination')
  if [[ -z "$src" || -z "$dst" || "$src" == "null" || "$dst" == "null" ]]; then
    echo "[WARN] Job $idx skipped (incorrect structure)." >&2
    continue
  fi
  echo "[JOB $idx/${TOTAL}] $src -> $dst"
  rclone sync "$src" "$dst" --config /config/rclone.conf --transfers 4 --verbose

done

echo "[INFO] Finished processing jobs."
