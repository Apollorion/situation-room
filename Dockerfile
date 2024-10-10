FROM python:bookworm

RUN pip install requests flask bs4

COPY . /app/

WORKDIR /app

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]