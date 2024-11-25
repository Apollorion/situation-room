FROM python:bookworm

RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN pip install requests flask bs4

COPY . /app/

WORKDIR /app

ENTRYPOINT ["/usr/bin/supervisord"]