FROM python:3.11-slim as build
WORKDIR /app
COPY . .

RUN pip install --no-cache-dir --upgrade pip pipenv

RUN apt-get update && apt-get upgrade -y && apt-get install -y git

COPY Pipfile* /
RUN pipenv install

ENTRYPOINT ["pipenv", "run", "patronload"]
