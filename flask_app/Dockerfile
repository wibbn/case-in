FROM python:3.7-alpine3.11 as base

FROM base AS builder

WORKDIR /opt/app

RUN apk add --no-cache jpeg-dev zlib-dev libffi-dev musl-dev gcc libgcc make

COPY requirements.txt /opt/app/requirements.txt

RUN pip install -r requirements.txt

FROM base

WORKDIR /opt/app

RUN apk add --no-cache jpeg zlib

COPY --from=builder /usr/local /usr/local

RUN ln -s /usr/share/zoneinfo/UTC /etc/localtime

ENV FLASK_CONFIG production

ENV WORKERS_NUM 3

ENV WORKER_TIMEOUT 1000

VOLUME /opt/app/instance

COPY ./ /opt/app/

EXPOSE 80

CMD gunicorn --bind 0.0.0.0:80 -w $WORKERS_NUM --log-level debug --timeout $WORKER_TIMEOUT -k gevent --preload manage:app