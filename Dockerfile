FROM python:3.8.1

ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

RUN set -ex \
    \
    && PYTHON_VERSION=2.7.16 \
    && PYTHON_SHA256=f222ef602647eecb6853681156d32de4450a2c39f4de93bd5b20235f2e660ed7 \
    && curl -sL -o python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-${PYTHON_VERSION}.tar.xz" \
    && echo "${PYTHON_SHA256} python.tar.xz" | sha256sum --check --status \
    && mkdir -p /usr/src/python \
    && tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
    && rm python.tar.xz \
    \
    && cd /usr/src/python \
    && gnuArch="$(dpkg-architecture --query DEB_BUILD_GNU_TYPE)" \
    && ./configure \
        --build="$gnuArch" \
        --enable-shared \
        --enable-unicode=ucs4 \
    && make -j "$(nproc)" \
    && make install \
    && ldconfig \
    \
    && find /usr/local -depth \
        \( \
            \( -type d -a \( -name test -o -name tests \) \) \
            -o \
            \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
        \) -exec rm -rf '{}' + \
    && rm -rf /usr/src/python \
    \
    && python2 --version

RUN set -ex; \
    \
    curl -sL -o get-pip.py 'https://bootstrap.pypa.io/pip/2.7/get-pip.py'; \
    \
    python2 get-pip.py \
        "pip==${PYTHON_PIP_VERSION}" \
    ; \
    pip2 --version; \
    \
    find /usr/local -depth \
        \( \
            \( -type d -a \( -name test -o -name tests \) \) \
            -o \
            \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
        \) -exec rm -rf '{}' +; \
    rm get-pip.py

RUN set -ex \
    \
    && cd /usr/local/bin \
    && rm python python-config pip \
    && ln -s python3 python \
    && ln -s pip3 pip \
    && ls -Fla /usr/local/bin/p* \
    && which python  && python -V \
    && which python2 && python2 -V \
    && which python3 && python3 -V \
    && which pip     && pip -V \
    && which pip2    && pip2 -V \
    && which pip3    && pip3 -V

RUN pip2 install virtualenv

# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r freight && useradd -r -m -g freight freight

ENV PYTHONUNBUFFERED 1

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

RUN set -x \
    && REDIS_VERSION=4.0.14 \
    && REDIS_SHA256=1e1e18420a86cfb285933123b04a82e1ebda20bfb0a289472745a087587e93a7 \
    && mkdir -p /usr/src/redis \
    && curl -sL -o redis.tar.gz "http://download.redis.io/releases/redis-${REDIS_VERSION}.tar.gz" \
    && echo "${REDIS_SHA256} *redis.tar.gz" | sha256sum --check --status \
    && tar -xzf redis.tar.gz -C /usr/src/redis --strip-components=1 \
    && rm redis.tar.gz \
    && make -C /usr/src/redis \
    && make -C /usr/src/redis install \
    && rm -r /usr/src/redis

# Install sentry-cli so the builds can register deploys, upload sourcemaps, etc.
RUN set -x \
    && SENTRY_CLI_VERSION=1.69.1 \
    && SENTRY_CLI_SHA256=4bed363e76e853aa1855b228b73b1e13a6b71209ce699bb0a117f98d6cfd8962 \
    && curl -sL -o /tmp/sentry-cli "https://github.com/getsentry/sentry-cli/releases/download/${SENTRY_CLI_VERSION}/sentry-cli-Linux-x86_64" \
    && echo "${SENTRY_CLI_SHA256} /tmp/sentry-cli" | sha256sum --check --status \
    && chmod +x /tmp/sentry-cli \
    && mv /tmp/sentry-cli /usr/local/bin

RUN set -x \
    && DOCKER_VERSION=18.03.1 \
    && DOCKER_SHA256=0e245c42de8a21799ab11179a4fce43b494ce173a8a2d6567ea6825d6c5265aa \
    && curl -sL -o docker.tgz "https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}-ce.tgz" \
    && echo "${DOCKER_SHA256} *docker.tgz" | sha256sum --check --status \
    && tar -zxvf docker.tgz \
    && mv docker/* /usr/local/bin/ \
    && rmdir docker \
    && rm docker.tgz \
    && docker -v

RUN set -x \
    && GCLOUD_VERSION=251.0.0 \
    && GCLOUD_SHA256=727fa0beae4c15b4b821f6df2381fbed8b2277b77fd74ebc721bd483b49541b5 \
    && curl -sL -o gcloud.tgz "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${GCLOUD_VERSION}-linux-x86_64.tar.gz" \
    && echo "${GCLOUD_SHA256} *gcloud.tgz" | sha256sum --check --status \
    && tar -zxvf gcloud.tgz -C /opt \
    && rm gcloud.tgz

RUN set -x \
    && KUBECTL_VERSION=v1.11.0 \
    && KUBECTL_SHA256=7fc84102a20aba4c766245714ce9555e3bf5d4116aab38a15b11419070a0fa90 \
    && curl -sL -o kubectl "https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    && echo "${KUBECTL_SHA256} *kubectl" | sha256sum --check --status \
    && install -m 755 kubectl /usr/local/bin/ \
    && kubectl --help

ENV PATH="${PATH}:/opt/google-cloud-sdk/bin"

ENV DOCKER_HOST tcp://docker:2375

COPY package.json /usr/src/app/
RUN npm install && npm cache clear --force

COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app
RUN node_modules/.bin/webpack -p \
    && pip install -e .

ENV WORKSPACE_ROOT /workspace
RUN mkdir -p $WORKSPACE_ROOT

ENV PATH /usr/src/app/bin:$PATH

EXPOSE 5000
VOLUME /workspace

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
CMD ["web", "--no-debug", "--addr", "0.0.0.0:5000"]
