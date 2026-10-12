#!/usr/bin/env bash
set -euo pipefail
: "${SMOKE_URL:?Set application health endpoint}"
case "$SMOKE_URL" in https://*|http://localhost:*|http://127.0.0.1:*) ;; *) echo "Unsupported smoke URL"; exit 1;; esac
for attempt in 1 2 3 4 5; do
  if curl --fail --silent --show-error --location --max-time 10 "$SMOKE_URL" >/dev/null; then
    echo "HTTP smoke check passed"
    exit 0
  fi
  sleep 3
done
echo "HTTP smoke check failed" >&2
exit 1
