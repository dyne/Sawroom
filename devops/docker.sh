#!/bin/sh

apt-get install \
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
apt-get update
apt-get install docker-ce docker-ce-cli containerd.io

# setup sawroom user
useradd -ms /bin/zsh sawroom
usermod -aG docker sawroom
mkdir -p /home/sawroom/.ssh /var/lib/sawroom
cp ~/.ssh/authorized_keys /home/sawroom/.ssh/
chown -R sawroom:sawroom /home/sawroom/.ssh /var/lib/sawroom
chsh sawroom -s /bin/zsh
cat <<EOF > /home/sawroom/.zshrc
#!/bin/sh
cd sawroom && ./shell
EOF
git clone https://github.com/dyne/sawroom /home/sawroom/sawroom

