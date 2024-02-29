FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml .

RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY . .

RUN openssl genrsa -out jwt-private.pem 2048
RUN openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
