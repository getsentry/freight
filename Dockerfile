FROM python:2.7

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN curl -sSL https://deb.nodesource.com/setup_0.12 -o setup_0.12 \
    && bash setup_0.12 \
    && rm setup_0.12 \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g npm@2.14.15 \
    && npm set progress=false

COPY package.json /usr/src/app/
RUN npm install

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app
RUN pip install --no-cache-dir -e .

EXPOSE 5000

CMD ["bin/web", "--no-debug", "--addr", "0.0.0.0:5000"]
