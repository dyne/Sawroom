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

ENV PATH=$PATH:/project/sawtooth-core/bin

WORKDIR /project


RUN curl -OLsS https://github.com/google/protobuf/releases/download/v3.5.1/protoc-3.5.1-linux-x86_64.zip \
	&& unzip protoc-3.5.1-linux-x86_64.zip -d protoc3 \
	&& cp -v protoc3/bin/protoc /usr/local/bin \
	&& rm -rf protoc-3.5.1-linux-x86_64.zip protoc3

# Sawtooth SDK
# RUN git clone https://github.com/hyperledger/sawtooth-sdk-python.git /project/sawtooth-sdk-python
RUN wget https://github.com/hyperledger/sawtooth-sdk-python/archive/v1.2.3.tar.gz \
	&& tar xf v1.2.3.tar.gz && ln -s sawtooth-sdk-python-1.2.3 sawtooth-sdk-python \
    && /project/sawtooth-sdk-python/bin/protogen \
	&& pip3 install -e /project/sawtooth-sdk-python \
	&& rm -rf v1.2.3.tar.gz sawtooth-sdk-python-1.2.3 sawtooth-sdk-python

# Petition transaction processor
# using latest zenroom-tp-python on git
RUN git clone https://github.com/DECODEproject/petition-tp-python /project/petition-tp-python \
	&& pip3 install -e /project/petition-tp-python/src

# install zenroom's cli binary and repo for tests
RUN wget https://files.dyne.org/zenroom/nightly/zenroom-linux-amd64 -O /usr/local/bin/zenroom && chmod +x /usr/local/bin/zenroom \
	&& git clone https://github.com/decodeproject/zenroom

# ## helper personas for the test units
# # .zen is code
# # .json is data
# # here alice and bob are two rounds of the coconut flow fully generated
# RUN cd /project/zenroom/test/zencode_coconut \
# 	&& cp *.zen /project/ \
# 	&& ./run_coconut_example.sh zenroom && ./run_petition_example.sh zenroom \
# 	&& mkdir -p /project/alice/ && cp -v *.json /project/alice/ \
# 	&& ./run_coconut_example.sh zenroom && ./run_petition_example.sh zenroom \
# 	&& mkdir -p /project/bob/ && cp -v *.json /project/bob/
# # sha256 sums are calculated to mark the difference by the two rounds.
# RUN cat alice/* | sha256sum - > alice.sha256 \
# 	&& cat bob/* | sha256sum - > bob.sha256

ENV PATH=$PATH:/project/petition-tp-python/bin

# installed later: must not be installed when compiling the sdk
RUN apt-get install -y -q libssl-dev libzmq3-dev torsocks

## Sawtooth Validator
RUN wget https://github.com/hyperledger/sawtooth-core/archive/v1.2.5.tar.gz \
	&& tar xvf v1.2.5.tar.gz && ln -s sawtooth-core-1.2.5 sawtooth-core \
	&& cd /project/sawtooth-core && ./bin/protogen \
	&& cd /project/sawtooth-core/validator && cargo build
# Install Sawtooth Validator (rust and python)
RUN cd /project/sawtooth-core && pip3 install -e validator \
	&& cp validator/target/debug/sawtooth-validator /usr/local/bin \
	&& cp validator/target/debug/libsawtooth_validator.so /usr/local/lib \
	&& ldconfig

## Sawtooth admin cli: sawadm and sawset
# RUN cd /project/sawtooth-core && pip3 install -e validator
RUN cd /project/sawtooth-core && pip3 install -e cli

RUN cd /project/sawtooth-core && pip3 install -e rest_api

RUN cd /project/sawtooth-core/families/settings/sawtooth_settings && cargo build \
	&& cp -v ./target/debug/settings-tp /usr/local/bin/settings-tp

RUN cd /project/sawtooth-core/families/block_info/sawtooth_block_info && cargo build \
	&& cp -v ./target/debug/block-info-tp /usr/local/bin/block-info-tp

# # temet nosce
# RUN apt-get install -y -q yarnpkg && yarnpkg add gatsby-cli npm
# RUN git clone https://github.com/DECODEproject/temet-nosce /project/temet-nosce \
# 	&& cd /project/temet-nosce && yarnpkg
# # CMD yarn start


RUN git clone https://github.com/hyperledger/sawtooth-devmode.git \
	sawtooth-devmode && cd /project/sawtooth-devmode \
	&& cargo build
RUN cp /project/sawtooth-devmode/target/debug/devmode-engine-rust /usr/local/bin

RUN wget https://github.com/hyperledger/sawtooth-pbft/archive/v1.0.3.tar.gz \
	&& tar xfz v1.0.3.tar.gz && ln -s sawtooth-pbft-1.0.3 sawtooth-pbft \
    && ls -l \
	&& cd /project/sawtooth-pbft \
    && cargo build
RUN cp /project/sawtooth-pbft/target/debug/pbft-engine /usr/local/bin
RUN apt-get install -y -q npm


ENV DYNESDK=https://sdk.dyne.org:4443/job \
	NETDATA_VERSION=1.10.0 \
	STEM_VERSION=1.6.0 \
	STEM_GIT=https://git.torproject.org/stem.git


# Tor repository
ADD https://raw.githubusercontent.com/DECODEproject/decode-os/master/docker-sdk/tor.pub.asc tor.pub.asc
RUN apt-key add tor.pub.asc
RUN echo "deb https://deb.torproject.org/torproject.org $debian main" >> /etc/apt/sources.list
RUN apt-get install -y -q golang redis-server redis-tools netdata tor nyx


RUN useradd -ms /bin/zsh sawroom

# Configure Tor Controlport auth
ENV	TORDAM_GIT=github.com/decodeproject/tor-dam
RUN torpass=`echo "print(OCTET.random(16):url64())" | zenroom` \
	&& go get -v -u $TORDAM_GIT/... && cd ~/go/src/github.com/decodeproject/tor-dam \
	&& sed -i python/damhs.py -e "s/topkek/$torpass/" \
	&& make install && make -C contrib install-init \
	&& torpasshash=`HOME=/var/lib/tor setuidgid debian-tor tor --quiet --hash-password "$torpass"` \
	&& sed -e 's/User tor/User sawroom/' < $HOME/go/src/$TORDAM_GIT/contrib/torrc > /etc/tor/torrc \
	&& sed -e 's/HashedControlPassword .*//' -i /etc/tor/torrc \
	&& echo "HashedControlPassword $torpasshash" >> /etc/tor/torrc \
	&& sed -e 's/Log notice .*/Log notice file \/var\/log\/tor\/tor.log/' -i /etc/tor/torrc

RUN chmod -R go-rwx /etc/tor && chown -R sawroom /etc/tor \
	&& rm -rf /var/lib/tor/data && chown -R sawroom /var/lib/tor \
	&& mkdir -p /var/run/tor && chown -R sawroom /var/run/tor
RUN cp /root/go/bin/dam* /usr/bin

WORKDIR /project

# petition transaction middleware
RUN pip3 install 'fastapi[all]' && pip3 install hypercorn


COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY sawroom-validator /usr/local/bin/sawroom-validator
COPY sawroom-start     /usr/local/bin/sawroom-start
COPY sawroom-list      /usr/local/bin/sawroom-list
COPY sawroom-address   /usr/local/bin/sawroom-address
COPY sawroom-seeds     /usr/local/bin/sawroom-seeds
COPY sawroom-genesis   /usr/local/bin/sawroom-genesis

RUN    echo "127.0.0.1 validator" >> /etc/hosts \
	&& echo "127.0.0.1 rest-api" >> /etc/hosts
CMD /etc/init.d/supervisor start

