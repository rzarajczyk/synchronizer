#!/usr/bin/env bash
set -euo pipefail

rclone version

# Ensure rclone configuration is available.
ensure_config() {
  local user_cfg_dir="$HOME/.config/rclone"
  local user_cfg_file="$user_cfg_dir/rclone.conf"
  mkdir -p "$user_cfg_dir"

  # If /config/rclone.conf is mounted, symlink it.
  if [[ -f /config/rclone.conf ]]; then
    ln -sf /config/rclone.conf "$user_cfg_file"
  # If the file is not in /config, but the user's exists and /config is writable, copy it for persistence.
  elif [[ -f "$user_cfg_file" && -w /config && ! -f /config/rclone.conf ]]; then
    cp "$user_cfg_file" /config/rclone.conf
  fi

  # Export absolute path (rclone honors RCLONE_CONFIG)
  if [[ -f "$user_cfg_file" ]]; then
    export RCLONE_CONFIG="$user_cfg_file"
  fi
}

ensure_config

echo : "${ACTION:=run}"
echo "$ACTION"


if [[ "${ACTION}" == "config" ]]; then
  rclone config
  ensure_config  # resynchronize after changes
  echo "----- ACTIVE rclone.conf -----"
  if [[ -f "$RCLONE_CONFIG" ]]; then
    cat "$RCLONE_CONFIG"
  else
    echo "Configuration file not found (RCLONE_CONFIG does not point to a file)." >&2
  fi
elif [[ "${ACTION}" == "run" ]]; then
  # Placeholder: this is where the synchronization logic will go; currently a test call
  rclone --version > /dev/null
  echo "Rclone ready (dry placeholder)."
fi