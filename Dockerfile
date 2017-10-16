FROM python:2.7.12

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
    && export GOSU_VERSION=1.10 \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true \
    && apt-get purge -y --auto-remove wget

# grab tini for signal processing and zombie killing
RUN set -x \
    && export TINI_VERSION=0.14.0 \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/v$TINI_VERSION/tini" \
    && wget -O /usr/local/bin/tini.asc "https://github.com/krallin/tini/releases/download/v$TINI_VERSION/tini.asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys 6380DC428747F6C393FEACA59A84159D7001A4E5 \
    && gpg --batch --verify /usr/local/bin/tini.asc /usr/local/bin/tini \
    && rm -r "$GNUPGHOME" /usr/local/bin/tini.asc \
    && chmod +x /usr/local/bin/tini \
    && tini -h \
    && apt-get purge -y --auto-remove wget

RUN set -x \
    && export NODE_VERSION=4.7.0 \
    && export GNUPGHOME="$(mktemp -d)" \
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
      gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$key"; \
    done \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.gz" \
    && wget "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
    && gpg --verify SHASUMS256.txt.asc \
    && grep " node-v$NODE_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
    && tar -xzf "node-v$NODE_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
    && rm -r "$GNUPGHOME" "node-v$NODE_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc \
    && apt-get purge -y --auto-remove wget

RUN set -x \
    && export REDIS_VERSION=3.2.6 \
    && export REDIS_DOWNLOAD_SHA1=0c7bc5c751bdbc6fabed178db9cdbdd948915d1b \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /usr/src/redis \
    && wget -O redis.tar.gz "http://download.redis.io/releases/redis-$REDIS_VERSION.tar.gz" \
    && echo "$REDIS_DOWNLOAD_SHA1 *redis.tar.gz" | sha1sum -c - \
    && tar -xzf redis.tar.gz -C /usr/src/redis --strip-components=1 \
    && rm redis.tar.gz \
    && make -C /usr/src/redis \
    && make -C /usr/src/redis install \
    && rm -r /usr/src/redis

RUN set -x \
    && export DOCKER_VERSION=1.13.1 \
    && export DOCKER_SHA256=97892375e756fd29a304bd8cd9ffb256c2e7c8fd759e12a55a6336e15100ad75 \
    && apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/* \
    && wget -O docker.tgz "https://get.docker.com/builds/Linux/x86_64/docker-$DOCKER_VERSION.tgz" \
    && echo "${DOCKER_SHA256} *docker.tgz" | sha256sum -c - \
    && tar -zxvf docker.tgz \
    && mv docker/* /usr/local/bin/ \
    && rmdir docker \
    && rm docker.tgz \
    && docker -v \
    && apt-get purge -y --auto-remove wget

ENV DOCKER_HOST tcp://docker:2375

COPY package.json /usr/src/app/
RUN npm install && npm cache clear

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
RUN node_modules/.bin/webpack -p \
    && pip install --no-cache-dir -e .

ENV WORKSPACE_ROOT /workspace
RUN mkdir -p $WORKSPACE_ROOT

ENV PATH /usr/src/app/bin:$PATH

EXPOSE 5000
VOLUME /workspace

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
CMD ["web", "--no-debug", "--addr", "0.0.0.0:5000"]
