all:

clean:
	rm -f sawroom.blend

sawroom.blend: clean
	cat extra/blend.head > $@
	docker2sh Dockerfile >> $@
	cat extra/blend.tail >> $@
