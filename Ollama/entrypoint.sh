#!/bin/bash
set -e
set -o pipefail

echo "Running entrypoint"

if [[ -z "$ANSWER_MODEL" ]]; then
    echo "No answer model specified to pull, exiting."
    exit 1
fi

if [[ -z "$EMBED_MODEL" ]]; then
    echo "No embed model specified to pull, exiting."
    exit 1
fi

OLLAMA_HOST=127.0.0.1:11545
/bin/ollama serve &
OLLAMA_PID=$!

SLEEP_TIME=1

until curl -s http://localhost:11545 > /dev/null; do
    echo "Ollama server not started, waiting $SLEEP_TIME second(s)"
    sleep $SLEEP_TIME
done

echo "Pulling $ANSWER_MODEL"
/bin/ollama pull $ANSWER_MODEL

echo "Pulling $EMBED_MODEL"
/bin/ollama pull $EMBED_MODEL

kill $OLLAMA_PID
wait $OLLAMA_PID 2>/dev/null || true

echo "Killed ollama instance for pulling"

export OLLAMA_HOST=127.0.0.1:11434