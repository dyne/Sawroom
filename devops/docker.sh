#!/bin/bash

apt-get install -y -q \
		git zsh \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
cat <<EOF > /etc/apt/sources.list.d/docker.list
deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable
EOF
apt-get update -y -q
apt-get -y -q install docker-ce docker-ce-cli containerd.io

# setup sawroom user
grep sawroom /etc/passwd
if [ $? = 1 ]; then
	useradd -ms /bin/zsh sawroom
	usermod -aG docker sawroom
fi
mkdir -p /home/sawroom/.ssh /var/lib/sawroom
cp ~/.ssh/authorized_keys /home/sawroom/.ssh/
chown -R sawroom:sawroom /var/lib/sawroom
chsh root -s /bin/zsh
chsh sawroom -s /bin/zsh
cat <<EOF > $HOME/.zshrc
#!/bin/sh
su - sawroom
EOF
cat <<EOF > /home/sawroom/.zshrc
#!/bin/sh
cd sawroom && ./shell
EOF
if ! [ -r /home/sawroom/sawroom ]; then
	git clone https://github.com/dyne/sawroom /home/sawroom/sawroom
fi
chown -R sawroom:sawroom /home/sawroom
