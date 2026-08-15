#!/usr/bin/env bash
# Render the preview in headless Chromium at a set of viewports/themes.
# Usage: tools/shoot.sh <label> [extra-query]
set -euo pipefail

CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
# New headless clamps the window to ~489px wide, which silently renders
# "mobile" shots at the wrong viewport. The old headless shell honours any size.
SHELL_BIN=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILE="file://$ROOT/preview/restrologic-preview.html?static=1"
OUT="$ROOT/shots"
LABEL="${1:-shot}"

mkdir -p "$OUT"

shoot() { # name width height
  local bin="$CHROME"
  [ "$2" -lt 520 ] && bin="$SHELL_BIN"
  "$bin" --headless --disable-gpu --no-sandbox --disable-dev-shm-usage \
    --hide-scrollbars --force-device-scale-factor=1 \
    --virtual-time-budget=8000 --window-size="$2,$3" \
    --screenshot="$OUT/$LABEL-$1.png" "$FILE" >/dev/null 2>&1
  echo "  $LABEL-$1.png  ($2x$3)"
}

shoot desktop 1440 10200
shoot tablet 820 12000
shoot mobile 390 13500
echo "done"
