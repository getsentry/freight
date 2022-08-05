FROM python:3.8.13-slim-bullseye

ARG VOLTA_VERSION=0.8.1
ARG VOLTA_SHA256=e1a45f073580552318c206069e5bf0dd8cb9dcdc1bfeaecc5a96c48a5208dd7a
ARG SENTRY_CLI_VERSION=1.69.1
ARG SENTRY_CLI_SHA256=4bed363e76e853aa1855b228b73b1e13a6b71209ce699bb0a117f98d6cfd8962
ARG DOCKER_CLI_VERSION=20.10.16
ARG DOCKER_CLI_SHA256=96588db31509c2a3c89eb68107b9bb9a0e6b1c9b5791e5c18475680d5074b40f
ARG GCLOUD_VERSION=382.0.0
ARG GCLOUD_SHA256=335e5a2b4099505372914acfccbb978cf9d4efd8047bda59f910c26daefd554e

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    VOLTA_HOME=/.volta \
    PATH="/usr/src/app/bin:/opt/google-cloud-sdk/bin:/.volta/bin:${PATH}"

# git's needed for Freight runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# This is the build user on cheffed and salted host machines
# that the Freight container should be run with.
# Directories that we volume mount when running Freight are owned by 9010:9010 (build).
RUN groupadd -g 9010 build && useradd -r -g 9010 -u 9010 build

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

# Install the node and yarn versions in package.json via volta.
COPY package.json .
RUN set -x \
    && curl -sL -o /tmp/volta.tar.gz "https://storage.googleapis.com/sentry-dev-infra-build-assets/volta-${VOLTA_VERSION}-linux-openssl-1.1.tar.gz" \
    && echo "$VOLTA_SHA256 /tmp/volta.tar.gz" | sha256sum --check --status \
    && tar -xz -C /usr/local/bin < /tmp/volta.tar.gz \
    && volta -v \
    && node -v \
    && yarn -v \
    && rm /tmp/volta.tar.gz

# Install sentry-cli so the builds can register deploys, upload sourcemaps, etc.
RUN set -x \
    && curl -sL -o /tmp/sentry-cli "https://github.com/getsentry/sentry-cli/releases/download/${SENTRY_CLI_VERSION}/sentry-cli-Linux-x86_64" \
    && echo "${SENTRY_CLI_SHA256} /tmp/sentry-cli" | sha256sum --check --status \
    && chmod +x /tmp/sentry-cli \
    && mv /tmp/sentry-cli /usr/local/bin

# Some builds, like Relay, rely on docker's cli for their sentry releases.
RUN set -x \
    && curl -sL -o /usr/local/bin/docker "https://storage.googleapis.com/sentry-dev-infra-build-assets/docker-${DOCKER_CLI_VERSION}" \
    && echo "${DOCKER_CLI_SHA256} /usr/local/bin/docker" | sha256sum --check --status \
    && chmod +x /usr/local/bin/docker \
    && docker -v

RUN set -x \
    && curl -sL -o gcloud.tgz "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${GCLOUD_VERSION}-linux-x86_64.tar.gz" \
    && echo "${GCLOUD_SHA256} *gcloud.tgz" | sha256sum --check --status \
    && tar -zxvf gcloud.tgz -C /opt \
    && rm gcloud.tgz

WORKDIR /usr/src/app

COPY package.json .
RUN yarn install && yarn cache clean --all

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN node_modules/.bin/webpack -p \
    && pip install -e .

ENV WORKSPACE_ROOT /workspace
RUN mkdir -p $WORKSPACE_ROOT

EXPOSE 5000
VOLUME $WORKSPACE_ROOT

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
CMD ["web", "--no-debug", "--addr", "0.0.0.0:5000"]
