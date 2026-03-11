FROM ollama/ollama:0.16.0

ARG ANSWER_MODEL="smollm:135m"
ARG EMBED_MODEL="jina/jina-embeddings-v2-small-en"

RUN apt-get update -y && apt-get install curl -y

COPY ./pull_models.sh /pull_models.sh

RUN chmod +x /pull_models.sh

RUN /pull_models.sh $ANSWER_MODEL $EMBED_MODEL

EXPOSE 11434

CMD ["serve"]
