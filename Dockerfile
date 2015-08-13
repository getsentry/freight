FROM python:2.7

RUN curl -sL https://deb.nodesource.com/setup | bash -
RUN apt-get -y install nodejs

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

RUN python setup.py develop
RUN npm install
RUN npm run postinstall

CMD ["bin/web", "--addr", "0.0.0.0:5000"]
