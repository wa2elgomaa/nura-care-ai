#!/usr/bin/env bash
# Sign and publish an update bundle to the local cloud-api.
# The private key is mounted into a ONE-OFF container only; the running cloud-api never sees it.
#
#   scripts/publish-update.sh <name> <version> <bundle-dir>
#   scripts/publish-update.sh rule-pack 1 ./bundles/demo
set -euo pipefail
[ $# -eq 3 ] || { echo "usage: $0 <name> <version> <bundle-dir>"; exit 2; }
NAME="$1"; VERSION="$2"; DIR="$(cd "$3" && pwd)"
[ -f secrets/update_signing_key.pem ] || { echo "missing secrets/update_signing_key.pem (README step 2)"; exit 1; }

docker compose --env-file .env --profile cloud run --rm --no-deps \
  -v "$PWD/secrets/update_signing_key.pem:/secrets/update_signing_key.pem:ro" \
  -v "$DIR:/bundle:ro" \
  -e SIGNING_KEY_FILE=/secrets/update_signing_key.pem \
  -e CLOUD_URL=http://cloud-api:8080 \
  cloud-api node dist/tools/publish.js --name "$NAME" --version "$VERSION" --dir /bundle
