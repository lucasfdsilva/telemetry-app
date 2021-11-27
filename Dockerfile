FROM python:3.7-alpine
LABEL maintainer="Lucas da Silva | lucas.silva00@outlook.ie"

RUN pip install --upgrade pip
RUN apk add --no-cache gcc
RUN apk add --no-cache libc-dev
RUN apk add --no-cache linux-headers

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app
COPY ./scripts /scripts
RUN chmod +x /scripts/*

CMD ["/scripts/entrypoint.sh"]