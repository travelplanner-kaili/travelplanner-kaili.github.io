#!/bin/bash
# Run once in a fresh workspace after cloning travelplanner-kaili.github.io into /home/claude/.
# The build scripts use absolute paths under /home/claude (lucca, rome, venice, shared...),
# so we link those names to the folders in this repo. Edits then land straight in git.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
for d in lucca rome venice shared; do
  if [ -e "/home/claude/$d" ] && [ ! -L "/home/claude/$d" ]; then echo "skip /home/claude/$d (a real folder is already there)"; continue; fi
  ln -sfn "$REPO/_src/$d" "/home/claude/$d"
done
for f in "$REPO"/_src/top/*.py; do ln -sfn "$f" "/home/claude/$(basename "$f")"; done
ln -sfn "$REPO/_src/spec.md" /home/claude/lucca/spec.md 2>/dev/null || true
(cd "$REPO/_src/lucca/real" && npm install --silent)                       # leaflet + sortablejs (inlined by the build)
ln -sfn "$REPO/_src/lucca/real/node_modules" "$REPO/_src/rome/real/node_modules"   # tests run from there too
pip install --break-system-packages -q numpy 2>/dev/null || true           # build_rome.py needs numpy
echo "ready: python3 /home/claude/lucca/real/build_real.py ; python3 /home/claude/rome/real/build_rome.py"
