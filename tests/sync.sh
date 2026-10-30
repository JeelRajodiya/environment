#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/home/.config" "$tmp/bin"
touch "$tmp/home/.config/keep"
mkdir -p "$tmp/home/.config/herdr-app"
touch "$tmp/home/.config/herdr-app/settings.json" "$tmp/home/.config/herdr-app/view.json"
printf '#!/bin/sh\ntouch "$HOME/stow-ran"\n' > "$tmp/bin/stow"
chmod +x "$tmp/bin/stow"

HOME="$tmp/home" PATH="$tmp/bin:$PATH" "$REPO_DIR/bin/sync.sh" >/dev/null

[ -f "$tmp/home/stow-ran" ]
[ -f "$tmp/home/.config/keep" ]
[ -L "$tmp/home/.config/herdr-app/settings.json" ]
[ -f "$tmp/home/.config/herdr-app/settings.json.pre-stow" ]
[ -f "$tmp/home/.config/herdr-app/view.json" ]
