FROM python:2.7

RUN curl -sL https://get.docker.com/ | bash -
RUN curl -sL https://github.com/docker/compose/releases/download/1.1.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose
RUN curl -sL https://github.com/docker/machine/releases/download/v0.1.0/docker-machine_linux-amd64 > /usr/local/bin/docker-machine
RUN chmod +x /usr/local/bin/docker-machine

RUN curl -sL https://deb.nodesource.com/setup | bash -
RUN apt-get -y install nodejs

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

VOLUME ["/usr/src/app/venv", "/usr/src/app/node_modules"]

ENTRYPOINT ["./docker-entrypoint"]
CMD ["bin/web", "--addr", "0.0.0.0:5000"]
