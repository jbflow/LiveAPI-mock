#!/bin/sh
# Regenerate Live/ from the LiveAPI stubs. Usage: scripts/regenerate.sh [live-version]  (default 12.3.6)
set -eu
version="${1:-12.3.6}"
root="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
git clone -q --depth 1 https://github.com/PhotonicVelocity/LiveAPI.git "$work/LiveAPI"
echo "stubs commit: $(git -C "$work/LiveAPI" rev-parse --short HEAD)"
python3 -I "$root/scripts/generate_live.py" "$work/LiveAPI/stubs/$version/Live" "$root/Live"
