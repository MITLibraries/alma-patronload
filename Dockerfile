FROM python:3.13-slim

# Set path for Oracle client libraries
ENV LD_LIBRARY_PATH=/opt/lib/

RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip libaio1t64 && \
    ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/libaio.so.1 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

# Install Oracle Instant Client
ENV INSTANTCLIENT_FILENAME=instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip
COPY vendor/$INSTANTCLIENT_FILENAME /
RUN unzip -j $INSTANTCLIENT_FILENAME -d /opt/lib/

WORKDIR /app

COPY pyproject.toml uv.lock* ./
COPY patronload ./patronload
COPY config ./config

RUN uv pip install --system .

ENTRYPOINT ["patronload"]
CMD []