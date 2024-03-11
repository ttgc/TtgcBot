FROM python:3.12.2-alpine3.19

USER root

ENV DEBIAN_FRONTEND=noninteractive

COPY ./ /

RUN apk update && \
    apk add gcc make libc-dev libffi-dev git && \
    python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt && \
    rm -rf ~/.cache/pip/* && \
    apk del gcc make libc-dev libffi-dev && \
    rm -rf /etc/apk/cache/*

CMD [ "./boot.sh" ]
