all:
	docker2sh ../Dockerfile \
		| sed -e 's/\\//g' \
		| sed -e 's/$$debian/buster/g' > sawroom.debian

