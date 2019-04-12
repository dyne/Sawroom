FROM ubuntu:bionic

RUN apt-get update \
 && apt-get install gnupg -y

RUN echo "deb http://repo.sawtooth.me/ubuntu/nightly bionic universe" >> /etc/apt/sources.list \
 && (apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 44FC67F19B2466EA \
 || apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 44FC67F19B2466EA) \
 && apt-get update

RUN apt-get install -y -q \
    git \
    python3 \
    python3-pip \
    python3-stdeb

RUN apt-get install -y -q \
    python3-grpcio \
    python3-grpcio-tools \
    python3-protobuf

RUN apt-get install -y -q \
    python3-cbor \
    python3-colorlog \
    python3-secp256k1 \
    python3-toml \
    python3-yaml \
    python3-zmq

RUN mkdir -p /var/log/sawtooth

RUN git clone https://github.com/hyperledger/sawtooth-sdk-python.git /project/sawtooth-sdk-python


COPY . /project/zenroom_tp_python
ENV PATH=$PATH:/project/zenroom_tp_python/bin


WORKDIR /project/sawtooth-sdk-python

RUN echo "\033[0;32m--- Building zenroom-tp-python ---\n\033[0m" \
 && /project/sawtooth-sdk-python/bin/protogen \
 && pip3 install -e /project/sawtooth-sdk-python \
 && pip3 install -e /project/zenroom_tp_python

CMD zenroom-tp-python
