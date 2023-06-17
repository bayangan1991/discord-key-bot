FROM python:3.10-slim
ENV POETRY_VERSION=1.5.1
WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN pip install "poetry==$POETRY_VERSION"  && \
    # Install into the main python installation
    poetry config virtualenvs.create false && \
    # Only prod dependencies and do not install current dir as a library
    poetry install --without dev --no-root --no-interaction --no-ansi && \
    # Remove poetry cache
    rm -rf /root/.cache/pypoetry

COPY . .
CMD ["python", "run.py"]