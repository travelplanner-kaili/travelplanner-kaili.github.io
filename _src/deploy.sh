#!/bin/bash
# Build and copy the real maps into the published folders. Then commit with a message that says WHY.
#   _src/deploy.sh lucca   |   _src/deploy.sh rome   |   _src/deploy.sh all
# Lucca note: build_rome.py also rebuilds Lucca locally, but Lucca is only published when asked for.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
what="${1:-all}"
python3 "$REPO/_src/lucca/real/build_real.py"
if [ "$what" = lucca ] || [ "$what" = all ]; then
  cp "$REPO/_src/lucca/real/lucca-real.html" "$REPO/lucca/index.html"; cp "$REPO/_src/lucca/real/version.json" "$REPO/lucca/"
fi
if [ "$what" = rome ] || [ "$what" = all ]; then
  python3 "$REPO/_src/rome/real/build_rome.py"
  cp "$REPO/_src/rome/real/rome-real.html" "$REPO/rome/index.html"; cp "$REPO/_src/rome/real/version.json" "$REPO/rome/"
fi
echo "copied. now: git add -A && git commit (explain the reason) && git -c push.negotiate=true push origin main"
