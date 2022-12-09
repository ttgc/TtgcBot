FROM python:3.10.4-alpine3.16

USER root

ENV DEBIAN_FRONTEND=noninteractive

COPY ./ /

RUN apk update && \
    apk add gcc make libc-dev libffi-dev git postgresql12 postgresql12-dev sudo openrc && \
    python3 -m pip install --upgrade pip && \
    pip3 install -r requirements.txt && \
    mkdir /run/postgresql && \
    chown postgres:postgres /run/postgresql/ && \
    sudo -u postgres mkdir /var/lib/postgresql/data && \
    sudo -u postgres chmod 0700 /var/lib/postgresql/data && \
    sudo -u postgres initdb -D /var/lib/postgresql/data && \
    touch /etc/local.d/postgres-custom.start && \
    chmod +x /etc/local.d/postgres-custom.start && \
    echo \#!/bin/sh > /etc/local.d/postgres-custom.start && \
    echo su postgres -c \'pg_ctl start -D /var/lib/postgresql/data\' >> /etc/local.d/postgres-custom.start && \
    rc-update add local default && \
    openrc && \
    /etc/local.d/postgres-custom.start && \
    sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE ttgcbot" && \
    sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE USER root ENCRYPTED PASSWORD 'root';" && \
    sudo -u postgres psql -v ON_ERROR_STOP=1 -c "GRANT ALL PRIVILEGES ON DATABASE ttgcbot TO root;" && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/tables.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/triggers.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/procedures.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/lang_features.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/userblock_features.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/pet.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/skill_and_kill_features.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/map.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/swap.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/jdr_rewrite.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/jdr_v4.sql && \
    psql -v ON_ERROR_STOP=1 -p 5432 -d ttgcbot -f database-scripts/jdr_v5.sql && \
    echo /etc/local.d/postgres-custom.start > startup.sh && \
    echo python3 TtgcBot.py staging >> startup.sh && \
    chmod +x startup.sh  && \
    rm -rf ~/.cache/pip/* && \
    apk del gcc make libc-dev libffi-dev && \
    rm -rf /etc/apk/cache/*

CMD ./startup.sh
