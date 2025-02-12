FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache wget curl tar git

ARG TARGETARCH
ENV SHOULTRRR_VERSION="v0.8.0"

RUN if [ "$TARGETARCH" = "amd64" ]; then \
        wget "https://github.com/containrrr/shoutrrr/releases/download/${SHOULTRRR_VERSION}/shoutrrr_linux_amd64.tar.gz" -O /tmp/shoutrrr.tar.gz; \
    elif [ "$TARGETARCH" = "arm64" ]; then \
        wget "https://github.com/containrrr/shoutrrr/releases/download/${SHOULTRRR_VERSION}/shoutrrr_linux_arm64.tar.gz" -O /tmp/shoutrrr.tar.gz; \
    else \
        echo "Unsupported architecture: ${TARGETARCH}" && exit 1; \
    fi && \
    tar -zxvf /tmp/shoutrrr.tar.gz -C /usr/local/bin/ && \
    chmod aug+x /usr/local/bin/shoutrrr && \
    rm /tmp/shoutrrr.tar.gz

RUN apk del wget tar

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shoutrrr-web.py .

ENV PORT=80

EXPOSE $PORT

HEALTHCHECK CMD curl --fail http://localhost:$PORT/health || exit 1

CMD ["python", "shoutrrr-web.py"]

