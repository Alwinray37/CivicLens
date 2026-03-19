    FROM python:3.12

    # RUN useradd -ms /bin/sh -u 1001 app
    # USER app

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install -r requirements.txt

    # COPY --chown=app:app . .
    COPY ./src ./src

    COPY ./entrypoint.sh /entrypoint.sh
    RUN chmod +x /entrypoint.sh

    ENTRYPOINT [ "/entrypoint.sh" ]

    EXPOSE 8000

    WORKDIR /app/src

    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
