#!/usr/bin/env bash
# Simulate loss of internet for the school box.
#   ./scripts/offline-test.sh down      # disconnect sync-agent from the uplink
#   ./scripts/offline-test.sh up        # reconnect (queued messages should drain)
#   ./scripts/offline-test.sh check     # show who is on the uplink + isolation test
set -euo pipefail
NET=nura_uplink_net
AGENT=nura-sync-agent

case "${1:-}" in
  down)  docker network disconnect "$NET" "$AGENT" && echo "OFFLINE: $AGENT disconnected from $NET" ;;
  up)    docker network connect "$NET" "$AGENT"    && echo "ONLINE: $AGENT reconnected to $NET" ;;
  check)
    echo "Containers on $NET (edge side should list only $AGENT):"
    docker network inspect "$NET" --format '{{range .Containers}}  {{.Name}}{{"\n"}}{{end}}'
    echo "Internet reachability from the core network (expected: FAIL):"
    if docker run --rm --network nura_core_net curlimages/curl:latest -sS -m 4 -o /dev/null https://example.com; then
      echo "  !! core_net can reach the internet - isolation is broken"; exit 1
    else
      echo "  OK: core_net has no internet route"
    fi ;;
  *) echo "usage: $0 {down|up|check}"; exit 2 ;;
esac
