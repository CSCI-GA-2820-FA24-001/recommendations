FROM rofrano/pipeline-selenium:latest

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN sudo python -m pip install --upgrade pip poetry && \
    sudo poetry config virtualenvs.create false && \
    sudo poetry install --without dev

COPY wsgi.py .
COPY service/ ./service/

RUN useradd --uid 1001 flask && chown -R flask /app
USER flask

# Expose any ports the app is expecting in the environment
ENV PORT=8080
EXPOSE $PORT

ENV GUNICORN_BIND=0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "wsgi:app"]