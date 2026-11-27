#!/usr/bin/env bash
# Capture one or more states of a standalone walkthrough HTML file via headless Chrome.
# Usage:
#   bash capture_walkthrough.sh <html-path> <out-dir> "name1:query1" "name2:query2" ...
# Example:
#   bash capture_walkthrough.sh notes/walkthrough.html /tmp/wt_qa \
#     "s1:scene=0" "s1_buried:scene=0&s1Layout=buried" "s2:scene=1"

set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <html-path> <out-dir> <name:query> [<name:query> ...]" >&2
  exit 1
fi

HTML_PATH="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT_DIR="$2"
shift 2

if [[ ! -f "$HTML_PATH" ]]; then
  echo "Error: HTML file not found: $HTML_PATH" >&2
  exit 1
fi

CHROME=""
for candidate in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "$(command -v google-chrome 2>/dev/null || true)" \
  "$(command -v chromium 2>/dev/null || true)" \
  "$(command -v chromium-browser 2>/dev/null || true)"; do
  if [[ -n "$candidate" && -x "$candidate" ]]; then
    CHROME="$candidate"
    break
  fi
done

if [[ -z "$CHROME" ]]; then
  echo "Error: Could not find Google Chrome or Chromium for headless capture." >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
FILE_URL="file://${HTML_PATH}"

for spec in "$@"; do
  name="${spec%%:*}"
  query="${spec#*:}"
  out_png="${OUT_DIR}/${name}.png"
  url="${FILE_URL}"
  if [[ -n "$query" && "$query" != "$spec" ]]; then
    url="${FILE_URL}?${query}"
  fi
  "$CHROME" \
    --headless=new \
    --disable-gpu \
    --window-size=1440,860 \
    --virtual-time-budget=1200 \
    --screenshot="$out_png" \
    "$url" 2>/dev/null
  echo "Captured $out_png ($url)"
done

FILTER_COUNT="$(grep -c 'filter="url(#' "$HTML_PATH" || true)"
echo "SVG filter=\"url(# count: ${FILTER_COUNT}"
