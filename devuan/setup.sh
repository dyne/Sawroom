#!/usr/bin/env zsh 

H="$1"
[[ "$H" == "" ]] && {
	print "Usage: ./setup.sh ssh@host.online.net"
	return 1
}

print "Installing sawroom on Debian version:"
ssh $H cat /etc/debian_version
ssh $H apt-get install -q -y git supervisor daemontools net-tools zsh curl unzip bzip2

# docker2sh script
ssh $H mkdir -p /project
scp sawroom.debian $H:
ssh $H bash sawroom.debian

# systemd shit
ssh $H systemctl disable redis-server
ssh $H systemctl disable tor
scp supervisord.service $H:/etc/systemd/system/
ssh $H chmod +x /etc/systemd/system/supervisord.service
ssh $H systemctl enable supervisord

# sawroom permissions
chmod a+x /usr/local/bin/*
mkdir -p /var/log/sawtooth /var/lib/sawroom /var/lib/sawtooth
chown -R sawroom:sawroom /var/log/sawtooth
chown -R sawroom:sawroom /var/lib/sawroom
chown -R sawroom:sawroom /var/lib/sawtooth
chown -R sawroom:sawroom /etc/sawtooth
mkdir -p /var/run/tor /var/lib/tor
chown -R sawroom:sawroom /var/run/tor
chown -R sawroom:sawroom /var/lib/tor
