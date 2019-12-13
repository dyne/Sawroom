FROM dyne/devuan:beowulf
ENV debian buster
ENV osarch amd64

LABEL maintainer="Denis Roio <jaromil@dyne.org>" \
	  homepage="https://sawroom.dyne.org"

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# use also security and updates from Devuan
RUN echo "deb http://pkgmaster.devuan.org/merged beowulf-security main" >> /etc/apt/sources.list
RUN echo "deb http://pkgmaster.devuan.org/merged beowulf-updates  main" >> /etc/apt/sources.list

RUN apt-get update -y -q \
	&& apt-get install -y -q \
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
    python3-stem \
    protobuf-compiler \
    protobuf-compiler-grpc \
    libffi-dev \
    supervisor daemontools net-tools \
    zsh wget curl unzip \
    && apt-get clean

RUN pip3 install grpcio-tools wheel

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

# Sawtooth SDK
# RUN git clone https://github.com/hyperledger/sawtooth-sdk-python.git /project/sawtooth-sdk-python
RUN wget https://github.com/hyperledger/sawtooth-sdk-python/archive/v1.2.2.tar.gz \
	&& tar xf v1.2.2.tar.gz && ln -s sawtooth-sdk-python-1.2.2 sawtooth-sdk-python \
    && /project/sawtooth-sdk-python/bin/protogen \
	&& pip3 install -e /project/sawtooth-sdk-python \
	&& rm -rf v1.2.2.tar.gz sawtooth-sdk-python-1.2.2 sawtooth-sdk-python

# Petition transaction processor
# using latest zenroom-tp-python on git
RUN git clone https://github.com/DECODEproject/sawroom /project/sawroom \
	&& pip3 install -e /project/sawroom/src/petition-tp

# install zenroom's cli binary and repo for tests
RUN wget https://sdk.dyne.org:4443/view/zenroom/job/zenroom-static-$osarch/lastSuccessfulBuild/artifact/src/zenroom -O /usr/local/bin/zenroom && chmod +x /usr/local/bin/zenroom \
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

# installed later: must not be installed when compiling the sdk
RUN apt-get install -y -q libssl-dev libzmq3-dev torsocks

## Sawtooth Validator
RUN wget https://github.com/hyperledger/sawtooth-core/archive/v1.3.0.tar.gz \
	&& tar xvf v1.3.0.tar.gz && ln -s sawtooth-core-1.3.0 sawtooth-core \
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

RUN wget https://github.com/hyperledger/sawtooth-pbft/archive/v1.0.0.tar.gz \
	&& tar xfz v1.0.0.tar.gz && ln -s sawtooth-pbft-1.0.0 sawtooth-pbft \
    && ls -l \
	&& cd /project/sawtooth-pbft \
    && cargo build
RUN cp /project/sawtooth-pbft/target/debug/pbft-engine /usr/local/bin

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

COPY src/supervisord.conf /etc/supervisor/supervisord.conf
COPY src/sawroom-validator /usr/local/bin/sawroom-validator
COPY src/sawroom-start     /usr/local/bin/sawroom-start
COPY src/sawroom-list      /usr/local/bin/sawroom-list
COPY src/sawroom-address   /usr/local/bin/sawroom-address
COPY src/sawroom-seeds     /usr/local/bin/sawroom-seeds
COPY src/sawroom-genesis   /usr/local/bin/sawroom-genesis

RUN chmod 775 /usr/local/bin/sawroom-*

RUN    echo "127.0.0.1 validator" >> /etc/hosts \
	&& echo "127.0.0.1 rest-api" >> /etc/hosts
CMD /etc/init.d/supervisor start