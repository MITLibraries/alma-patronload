FROM python:3.13-slim

# Set path for Oracle client libraries
ENV LD_LIBRARY_PATH=/opt/lib/

RUN apt-get update && apt-get upgrade -y

# Install Oracle dependencies
RUN apt-get install -y unzip libaio1t64 git ca-certificates
RUN ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/libaio.so.1
ENV INSTANTCLIENT_FILENAME=instantclient-basiclite-linux.x64-21.9.0.0.0dbru.zip
COPY vendor/$INSTANTCLIENT_FILENAME /
RUN unzip -j $INSTANTCLIENT_FILENAME -d /opt/lib/

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY patronload ./patronload

# Install Python dependencies
RUN uv pip install --system .

# App entrypoint and default command
ENTRYPOINT ["patronload"]
CMD []