FROM python:3.8.12

ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONUNBUFFERED 1
ENV PATH="/usr/src/app/bin:${PATH}:/opt/google-cloud-sdk/bin"

# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r freight && useradd -r -m -g freight freight

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y --no-install-recommends \
        unzip \
        zip \
    && rm -rf /var/lib/apt/lists/*

# grab gosu for easy step-down from root
RUN set -x \
    && GOSU_VERSION=1.11 \
    && GOSU_SHA256=0b843df6d86e270c5b0f5cbd3c326a04e18f4b7f9b8457fa497b0454c4b138d7 \
    && curl -sL -o /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-$(dpkg --print-architecture)" \
    && echo "${GOSU_SHA256} /usr/local/bin/gosu" | sha256sum --check --status \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true

# grab tini for signal processing and zombie killing
RUN set -x \
    && TINI_VERSION=0.18.0 \
    && TINI_SHA256=12d20136605531b09a2c2dac02ccee85e1b874eb322ef6baf7561cd93f93c855 \
    && curl -sL -o /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini" \
    && echo "${TINI_SHA256} /usr/local/bin/tini" | sha256sum --check --status \
    && chmod +x /usr/local/bin/tini \
    && tini -h

RUN set -x \
    && NODE_VERSION=8.15.1 \
    && NODE_SHA256=16e203f2440cffe90522f1e1855d5d7e2e658e759057db070a3dafda445d6d1f \
    && curl -sL -o "node-linux-x64.tar.gz" "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.gz" \
    && echo "${NODE_SHA256} node-linux-x64.tar.gz" | sha256sum --check --status \
    && tar -xzf "node-linux-x64.tar.gz" -C /usr/local --strip-components=1

# Install sentry-cli so the builds can register deploys, upload sourcemaps, etc.
RUN set -x \
    && SENTRY_CLI_VERSION=1.69.1 \
    && SENTRY_CLI_SHA256=4bed363e76e853aa1855b228b73b1e13a6b71209ce699bb0a117f98d6cfd8962 \
    && curl -sL -o /tmp/sentry-cli "https://github.com/getsentry/sentry-cli/releases/download/${SENTRY_CLI_VERSION}/sentry-cli-Linux-x86_64" \
    && echo "${SENTRY_CLI_SHA256} /tmp/sentry-cli" | sha256sum --check --status \
    && chmod +x /tmp/sentry-cli \
    && mv /tmp/sentry-cli /usr/local/bin

RUN set -x \
    && GCLOUD_VERSION=251.0.0 \
    && GCLOUD_SHA256=727fa0beae4c15b4b821f6df2381fbed8b2277b77fd74ebc721bd483b49541b5 \
    && curl -sL -o gcloud.tgz "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${GCLOUD_VERSION}-linux-x86_64.tar.gz" \
    && echo "${GCLOUD_SHA256} *gcloud.tgz" | sha256sum --check --status \
    && tar -zxvf gcloud.tgz -C /opt \
    && rm gcloud.tgz

COPY package.json /usr/src/app/
RUN npm install && npm cache clear --force

COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app
RUN node_modules/.bin/webpack -p \
    && pip install -e .

ENV WORKSPACE_ROOT /workspace
RUN mkdir -p $WORKSPACE_ROOT

EXPOSE 5000
VOLUME /workspace

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
CMD ["web", "--no-debug", "--addr", "0.0.0.0:5000"]
