#!/usr/bin/env bash
# Helpers to talk to the sync-agent (reachable on the core network only).
#   scripts/agent.sh status
#   scripts/agent.sh enqueue '{"type":"alert.violation","payload":{"rule":"R-0042","room":"3"}}'
#   scripts/agent.sh events            # what the cloud has received
#   scripts/agent.sh devices           # device registry / last seen
set -euo pipefail
ENVF=.env; [ -f "$ENVF" ] && set -a && . "$ENVF" && set +a
TOKEN="${CLOUD_ADMIN_TOKEN:-change-me-dev-only}"
PORT="${CLOUD_API_PORT:-8081}"
core() { docker run --rm --network nura_core_net curlimages/curl:latest -sS "$@"; echo; }
case "${1:-}" in
  status)  core http://sync-agent:7070/status ;;
  enqueue) core -XPOST http://sync-agent:7070/enqueue -d "${2:?json body required}" ;;
  events)  curl -sS -H "x-admin-token: $TOKEN" "http://localhost:$PORT/v1/admin/events?limit=${2:-20}"; echo ;;
  devices) curl -sS -H "x-admin-token: $TOKEN" "http://localhost:$PORT/v1/admin/devices"; echo ;;
  *) echo "usage: $0 {status|enqueue <json>|events [n]|devices}"; exit 2 ;;
esac
