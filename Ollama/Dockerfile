FROM ollama/ollama:0.16.0

RUN apt-get update -y && apt-get install curl -y

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 11434

ENTRYPOINT [ "bin/sh", "-c", "/entrypoint.sh && /bin/ollama serve" ]