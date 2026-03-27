#!/bin/bash
set -e
set -o pipefail

echo "Running API entrypoint"

if [[ -z "$OLLAMA_CONN" ]]; then
    echo "No ollama connection string specified, exiting."
    exit 1
fi

SLEEP_TIME=1

until curl -s $OLLAMA_CONN > /dev/null; do
    echo "Waiting for Ollama server on ${OLLAMA_CONN}..."
    sleep $SLEEP_TIME
done

exec "$@"