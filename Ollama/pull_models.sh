#!/bin/bash
set -e
set -o pipefail

echo "Running entrypoint"

if [[ -z "$1" ]]; then
    echo "No models specified to pull, exiting."
    exit 1
fi

OLLAMA_HOST=127.0.0.1:11545
/bin/ollama serve &
OLLAMA_PID=$!

sleep_time=1

until curl -s http://localhost:11545 > /dev/null; do
    echo "Ollama server not started, waiting $sleep_time second(s)"
    sleep $sleep_time
done

for model in "$@"; do
    echo "Pulling $model"
    /bin/ollama pull $model
done

kill $OLLAMA_PID
wait $OLLAMA_PID 2>/dev/null || true

OLLAMA_HOST=127.0.0.1:11434