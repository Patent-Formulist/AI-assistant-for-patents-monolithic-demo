#!/bin/sh
# Register the application namespace once the server accepts requests. Safe to re-run.
set -eu
ADDRESS="${TEMPORAL_ADDRESS:-temporal:7233}"
NAMESPACE="${TEMPORAL_NAMESPACE:-default}"
for i in $(seq 1 30); do
  temporal operator cluster health --address "$ADDRESS" >/dev/null 2>&1 && break
  echo "waiting for temporal at $ADDRESS ($i)"; sleep 2
done
if temporal operator namespace describe --address "$ADDRESS" --namespace "$NAMESPACE" >/dev/null 2>&1; then
  echo "namespace $NAMESPACE exists"
else
  temporal operator namespace create --address "$ADDRESS" --namespace "$NAMESPACE" \
    --retention "${TEMPORAL_RETENTION:-72h}"
  echo "namespace $NAMESPACE created"
fi
