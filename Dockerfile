FROM python:3.7.3

ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

RUN set -ex \
    \
    && PYTHON_VERSION=2.7.16 \
    && wget -O python.tar.xz "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" \
    && wget -O python.tar.xz.asc "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && for key in \
      C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF \
    ; do \
      gpg --batch --keyserver hkps://mattrobenolt-keyserver.global.ssl.fastly.net:443 --recv-keys "$key" ; \
    done \
    && gpg --batch --verify python.tar.xz.asc python.tar.xz \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" python.tar.xz.asc \
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
    wget -O get-pip.py 'https://bootstrap.pypa.io/get-pip.py'; \
    \
    python2 get-pip.py \
        "pip==$PYTHON_PIP_VERSION" \
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
    && export GOSU_VERSION=1.11 \
    && fetchDeps=" \
        dirmngr \
        gnupg \
        wget \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $fetchDeps && rm -rf /var/lib/apt/lists/* \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && for key in \
      B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    ; do \
      gpg --batch --keyserver hkps://mattrobenolt-keyserver.global.ssl.fastly.net:443 --recv-keys "$key" ; \
    done \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && gpgconf --kill all \
    && rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true \
    && apt-get purge -y --auto-remove $fetchDeps

# grab tini for signal processing and zombie killing
RUN set -x \
    && export TINI_VERSION=0.18.0 \
    && fetchDeps=" \
        dirmngr \
        gnupg \
        wget \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $fetchDeps && rm -rf /var/lib/apt/lists/* \
    && wget -O /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/v$TINI_VERSION/tini" \
    && wget -O /usr/local/bin/tini.asc "https://github.com/krallin/tini/releases/download/v$TINI_VERSION/tini.asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && for key in \
      595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 \
    ; do \
      gpg --batch --keyserver hkps://mattrobenolt-keyserver.global.ssl.fastly.net:443 --recv-keys "$key" ; \
    done \
    && gpg --batch --verify /usr/local/bin/tini.asc /usr/local/bin/tini \
    && gpgconf --kill all \
    && rm -r "$GNUPGHOME" /usr/local/bin/tini.asc \
    && chmod +x /usr/local/bin/tini \
    && tini -h \
    && apt-get purge -y --auto-remove $fetchDeps

RUN set -x \
    && export NODE_VERSION=8.15.1 \
    && export GNUPGHOME="$(mktemp -d)" \
    && fetchDeps=" \
        dirmngr \
        gnupg \
        wget \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $fetchDeps && rm -rf /var/lib/apt/lists/* \
    # gpg keys listed at https://github.com/nodejs/node
    && for key in \
      9554F04D7259F04124DE6B476D5A82AC7E37093B \
      94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
      0034A06D9D9B0064CE8ADF6BF1747F4AD2306D93 \
      FD3A5288F042B6850C66B31F09FE44734EB7990E \
      71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
      DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
      B9AE9905FFD7803F25714661B63B535A4C206CA9 \
      C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
    ; do \
      gpg --batch --keyserver hkps://mattrobenolt-keyserver.global.ssl.fastly.net:443 --recv-keys "$key" ; \
    done \
    && wget "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.gz" \
    && wget "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
    && gpg --batch --verify SHASUMS256.txt.asc \
    && gpgconf --kill all \
    && grep " node-v$NODE_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
    && tar -xzf "node-v$NODE_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
    && rm -r "$GNUPGHOME" "node-v$NODE_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc \
    && apt-get purge -y --auto-remove $fetchDeps

RUN set -x \
    && export REDIS_VERSION=4.0.14 \
    && export REDIS_DOWNLOAD_SHA256=1e1e18420a86cfb285933123b04a82e1ebda20bfb0a289472745a087587e93a7 \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /usr/src/redis \
    && wget -O redis.tar.gz "http://download.redis.io/releases/redis-$REDIS_VERSION.tar.gz" \
    && echo "$REDIS_DOWNLOAD_SHA256 *redis.tar.gz" | sha256sum -c - \
    && tar -xzf redis.tar.gz -C /usr/src/redis --strip-components=1 \
    && rm redis.tar.gz \
    && make -C /usr/src/redis \
    && make -C /usr/src/redis install \
    && rm -r /usr/src/redis \
    && apt-get purge -y --auto-remove wget

# Install sentry-cli so the builds can register deploys, upload sourcemaps, etc.
RUN set -x \
    && export SENTRY_CLI_VERSION=1.40.0 \
    && export SENTRY_CLI_SHA256=3312dbd7d4f7cec8f1980ba09ef741eadfa5d74315fac6f09812e4b307740432 \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O /tmp/sentry-cli "https://github.com/getsentry/sentry-cli/releases/download/$SENTRY_CLI_VERSION/sentry-cli-Linux-x86_64" \
    && echo "$SENTRY_CLI_SHA256 /tmp/sentry-cli" | sha256sum -c - \
    && chmod +x /tmp/sentry-cli \
    && mv /tmp/sentry-cli /usr/local/bin \
    && apt-get purge -y --auto-remove wget

RUN set -x \
    && export DOCKER_VERSION=18.03.1 \
    && export DOCKER_SHA256=0e245c42de8a21799ab11179a4fce43b494ce173a8a2d6567ea6825d6c5265aa \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O docker.tgz "https://download.docker.com/linux/static/stable/x86_64/docker-$DOCKER_VERSION-ce.tgz" \
    && echo "${DOCKER_SHA256} *docker.tgz" | sha256sum -c - \
    && tar -zxvf docker.tgz \
    && mv docker/* /usr/local/bin/ \
    && rmdir docker \
    && rm docker.tgz \
    && docker -v \
    && apt-get purge -y --auto-remove wget

RUN set -x \
    && export GCLOUD_SHA256=71229c3cd2290a60310c5ac9fb2e660cb1a4a0f637704b4b3af0a1f75f649e5f \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O gcloud.tgz "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-201.0.0-linux-x86_64.tar.gz" \
    && echo "${GCLOUD_SHA256} *gcloud.tgz" | sha256sum -c - \
    && tar -zxvf gcloud.tgz -C /opt \
    && rm gcloud.tgz \
    && apt-get purge -y --auto-remove wget

RUN set -x \
    && export KUBECTL_VERSION=v1.11.0 \
    && export KUBECTL_SHA256=7fc84102a20aba4c766245714ce9555e3bf5d4116aab38a15b11419070a0fa90 \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O kubectl "https://storage.googleapis.com/kubernetes-release/release/$KUBECTL_VERSION/bin/linux/amd64/kubectl" \
    && echo "${KUBECTL_SHA256} *kubectl" | sha256sum -c - \
    && install -m 755 kubectl /usr/local/bin/ \
    && kubectl --help \
    && apt-get purge -y --auto-remove wget

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
