#!/usr/bin/env bash
# Usage: score.sh <repo-dir>  -> runs public tests and hidden tests, prints per-test results
set -u
here=$(cd "$(dirname "$0")" && pwd)
d="$1"
tmp=$(mktemp -d)
cp -r "$d" "$tmp/repo"
mkdir -p "$tmp/repo/hidden"
cp "$here/hidden/test_hidden.py" "$tmp/repo/hidden/"
cd "$tmp/repo"
echo "== public =="
python3 -m pytest -q tests 2>&1 | tail -3
echo "== hidden =="
python3 -m pytest -q hidden -p no:cacheprovider -rA 2>&1 | grep -E "^(PASSED|FAILED|ERROR)" | sed 's/ - .*//' | sort
python3 -m pytest -q hidden -p no:cacheprovider 2>&1 | tail -1
rm -rf "$tmp"
