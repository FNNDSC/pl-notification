# Python version can be changed, e.g.
FROM docker.io/python:3.11.3-slim-bullseye

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="An email plugin" \
      org.opencontainers.image.description="A ChRIS Plugin for notification through mail / Slack / Element"

ARG SRCDIR=/usr/local/src/pl-notification
RUN mkdir -p ${SRCDIR}
WORKDIR ${SRCDIR}

COPY . .
RUN pip install "." \
    && cd /
WORKDIR /

CMD ["notification"]
