FROM dyne/devuan:beowulf
ENV debian buster

LABEL maintainer="Denis Roio <jaromil@dyne.org>" \
	  homepage="https://sawroom.dyne.org"

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN apt-get update -y -q \
	&& apt-get install -y -q \
    g++ \
    pkg-config \
    python3 \
    python3-pip \
    python3-stdeb \
	python3-dev \
    python3-protobuf \
    python3-cbor \
    python3-colorlog \
    python3-toml \
    python3-yaml \
    python3-zmq \
    python3-grpcio \
    python3-grpc-tools \
    supervisor daemontools net-tools \
	zsh curl unzip \
    && apt-get clean

RUN pip3 install wheel

RUN curl https://sh.rustup.rs -sSf > /usr/bin/rustup-init \
 && chmod +x /usr/bin/rustup-init \
 && rustup-init -y

ENV PATH=$PATH:/project/sawtooth-core/bin:/protoc3/bin:/project/sawtooth-core/bin:/root/.cargo/bin \
	CARGO_INCREMENTAL=0

RUN mkdir -p /etc/sawtooth/keys \
	&& mkdir -p /var/lib/sawtooth \
	&& mkdir -p /var/log/sawtooth

ENV PATH=$PATH:/project/sawtooth-core/bin \
	DYNESDK=https://sdk.dyne.org:4443/job \
	STEM_VERSION=1.6.0 \
	STEM_GIT=https://git.torproject.org/stem.git \
    PROTOBUF_VERSION=3.14.0 \
    SAWTOOTH_SDK_VERSION=1.2.3 \
    SAWTOOTH_CORE_VERSION=1.2.6 \
    SAWTOOTH_PBFT_VERSION=1.0.3

WORKDIR /project

RUN cd /project && \
	curl -OLsS https://github.com/protocolbuffers/protobuf/releases/download/v$PROTOBUF_VERSION/protoc-$PROTOBUF_VERSION-linux-x86_64.zip \
	&& unzip protoc-$PROTOBUF_VERSION-linux-x86_64.zip -d protoc3 \
	&& cp -v protoc3/bin/protoc /usr/local/bin \
	&& rm -rf protoc-$PROTOBUF_VERSION-linux-x86_64.zip protoc3

# Sawtooth SDK
# RUN git clone https://github.com/hyperledger/sawtooth-sdk-python.git /project/sawtooth-sdk-python
RUN cd /project && \
	wget https://github.com/hyperledger/sawtooth-sdk-python/archive/v$SAWTOOTH_SDK_VERSION.tar.gz \
	&& tar xf v$SAWTOOTH_SDK_VERSION.tar.gz && \
	ln -s sawtooth-sdk-python-$SAWTOOTH_SDK_VERSION sawtooth-sdk-python \
    && /project/sawtooth-sdk-python/bin/protogen \
	&& pip3 install -e /project/sawtooth-sdk-python \
	&& rm -rf v$SAWTOOTH_SDK_VERSION.tar.gz sawtooth-sdk-python-$SAWTOOTH_SDK_VERSION sawtooth-sdk-python

# Petition transaction processor
# using latest zenroom-tp-python on git

RUN cd /project && \
	git clone https://github.com/dyne/petition-tp-python /project/petition-tp-python \
	&& pip3 install -e /project/petition-tp-python/src
ENV PATH=$PATH:/project/petition-tp-python/bin

# install zenroom's cli binary and repo for tests
RUN cd /project && \
	wget https://files.dyne.org/zenroom/nightly/zenroom-linux-amd64 -O /usr/local/bin/zenroom && chmod +x /usr/local/bin/zenroom


# installed later: must not be installed when compiling the sdk
RUN apt-get install -y -q libssl-dev libzmq3-dev torsocks
# dep of sawtooth-core and transaction processor
RUN pip3 install sawtooth-signing

## Install the storage-rust-tp
WORKDIR /project
RUN git clone https://github.com/dyne/sawroom-storage-tp
WORKDIR /project/sawroom-storage-tp
RUN cargo build --release
RUN cp -v ./target/release/storage-tp /usr/local/bin

## install the sawroom-wallet-tp
WORKDIR /project
RUN git clone https://github.com/dyne/sawroom-wallet-tp
WORKDIR /project/sawroom-wallet-tp
RUN cargo build --release
RUN cp -v ./target/release/sawroom-wallet-tp /usr/local/bin

## Sawtooth Validator
RUN cd /project && \
	wget https://github.com/hyperledger/sawtooth-core/archive/v$SAWTOOTH_CORE_VERSION.tar.gz \
	&& tar xvf v$SAWTOOTH_CORE_VERSION.tar.gz && ln -s sawtooth-core-$SAWTOOTH_CORE_VERSION sawtooth-core \
	&& cd /project/sawtooth-core && ./bin/protogen \
	&& cd /project/sawtooth-core/validator \
	&& sed -i -e 's/heartbeat_interval=10/heartbeat_interval=60/' \
	-e 's/connection_timeout=60/connection_timeout=360/' \
	sawtooth_validator/networking/interconnect.py \
	&& cargo build --color never --release
# Install Sawtooth Validator (rust and python)
RUN cd /project/sawtooth-core && pip3 install -e validator \
	&& cp validator/target/release/sawtooth-validator /usr/local/bin \
	&& cp validator/target/release/libsawtooth_validator.so /usr/local/lib \
	&& ldconfig

## Sawtooth admin cli: sawadm and sawset
# RUN cd /project/sawtooth-core && pip3 install -e validator
RUN cd /project/sawtooth-core && pip3 install -e cli

RUN cd /project/sawtooth-core && pip3 install -e rest_api

RUN cd /project/sawtooth-core/families/settings/sawtooth_settings && cargo build --color never --release \
	&& cp -v ./target/release/settings-tp /usr/local/bin/settings-tp

RUN cd /project/sawtooth-core/families/block_info/sawtooth_block_info && cargo build --color never --release \
	&& cp -v ./target/release/block-info-tp /usr/local/bin/block-info-tp

RUN cd /project/sawtooth-core/families/identity/sawtooth_identity && cargo build --color never --release \
	&& cp -v ./target/release/identity-tp /usr/local/bin/identity-tp

# # temet nosce
# RUN apt-get install -y -q yarnpkg && yarnpkg add gatsby-cli npm
# RUN git clone https://github.com/DECODEproject/temet-nosce /project/temet-nosce \
# 	&& cd /project/temet-nosce && yarnpkg
# # CMD yarn start


RUN cd /project && \
	git clone https://github.com/hyperledger/sawtooth-devmode.git \
	sawtooth-devmode && cd /project/sawtooth-devmode \
	&& cargo build --color never --release
RUN cp /project/sawtooth-devmode/target/release/devmode-engine-rust /usr/local/bin

RUN cd /project && \
	wget https://github.com/hyperledger/sawtooth-pbft/archive/v$SAWTOOTH_PBFT_VERSION.tar.gz \
	&& tar xfz v$SAWTOOTH_PBFT_VERSION.tar.gz && ln -s sawtooth-pbft-$SAWTOOTH_PBFT_VERSION sawtooth-pbft \
    && ls -l \
	&& cd /project/sawtooth-pbft \
    && cargo build --color never --release
RUN cp /project/sawtooth-pbft/target/release/pbft-engine /usr/local/bin


# Tor repository
ADD https://raw.githubusercontent.com/DECODEproject/decode-os/master/docker-sdk/tor.pub.asc tor.pub.asc
RUN apt-key add tor.pub.asc
RUN echo "deb https://deb.torproject.org/torproject.org $debian main" > /etc/apt/sources.list.d/tor.list
RUN apt-get install -y -q redis-server redis-tools tor nyx

RUN useradd -ms /bin/zsh sawroom

ENV	TORDAM_GIT=github.com/dyne/tor-dam

# Download latest tor-dam binaries from files.dyne.org
RUN wget -q https://files.dyne.org/tor-dam/nightly/dam-client  \
	&& wget -q https://files.dyne.org/tor-dam/nightly/dam-dir  \
	&& mv dam-* /usr/local/bin && chmod a+x /usr/local/bin/dam-*

# Configure Tor Controlport auth
COPY src/torrc /etc/tor/torrc
RUN torpass=`echo "print(OCTET.random(16):url64())" | zenroom` \
    && git clone https://$TORDAM_GIT && cd tor-dam \
	&& sed -i python/damhs.py -e "s/topkek/$torpass/" \
	&& make install && make -C contrib install-init \
    && torpasshash=`HOME=/var/lib/tor setuidgid debian-tor tor --hash-password "$torpass"` \
	&& sed -e 's/HashedControlPassword .*//' -i /etc/tor/torrc \
	&& echo "HashedControlPassword $torpasshash" >> /etc/tor/torrc \
	&& sed -e 's/Log notice .*/Log notice file \/var\/log\/tor\/tor.log/' -i /etc/tor/torrc

RUN chmod -R go-rwx /etc/tor && chown -R sawroom:sawroom /etc/tor \
	&& rm -rf /var/lib/tor/data && mkdir -p /var/lib/tor/dam \
	&& chown -R sawroom:sawroom /var/lib/tor \
	&& chown -R sawroom:sawroom /etc/sawtooth \
	&& chmod o-rwx /etc/sawtooth/keys

# Configure the network time protocol daemon and logrotate
RUN apt-get -y -q install cron openntpd logrotate

WORKDIR /project

# petition transaction middleware
RUN pip3 install 'fastapi[all]' && pip3 install hypercorn

# SAWROOM BUILD CONFIGURATION
ENV SAWROOM_TRACKERS https://sawroom.dyne.org/testnet.txt
# ENV SAWROOM_GENESIS  https://sawroom.dyne.org/testnet-genesis.txt
ENV SAWROOM_NETWORK IP4

RUN echo $SAWROOM_TRACKERS > /etc/SAWROOM_TRACKERS
# RUN echo $SAWROOM_GENESIS  > /etc/SAWROOM_GENESIS
RUN echo $SAWROOM_NETWORK  > /etc/SAWROOM_NETWORK
COPY src/logrotate.conf    /etc/logrotate.d/sawtooth
COPY src/supervisord.conf  /etc/supervisor/supervisord.conf
COPY src/sawroom-validator /usr/local/bin/sawroom-validator
COPY src/sawroom-start     /usr/local/bin/sawroom-start
COPY src/sawroom-list      /usr/local/bin/sawroom-list
COPY src/sawroom-address   /usr/local/bin/sawroom-address
COPY src/sawroom-seeds     /usr/local/bin/sawroom-seeds
COPY src/genesis-create    /usr/local/bin/genesis-create
COPY src/genesis-import    /usr/local/bin/genesis-import
COPY src/genesis-export    /usr/local/bin/genesis-export
COPY src/keys-create       /usr/local/bin/keys-create
COPY src/keys-export       /usr/local/bin/keys-export
COPY src/dam-start         /usr/local/bin/dam-start
COPY src/update-tp         /usr/local/bin/update-tp

RUN    echo "127.0.0.1 validator" >> /etc/hosts \
	&& echo "127.0.0.1 rest-api" >> /etc/hosts

CMD /etc/init.d/supervisor start

