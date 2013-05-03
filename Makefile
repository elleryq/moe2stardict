
all: moedict.ifo

# tools
sym.txt:
	wget https://github.com/g0v/moedict-epub/raw/master/sym.txt -O $@

json2unicode.pl: sym.txt
	wget https://github.com/g0v/moedict-epub/raw/master/json2unicode.pl -O $@

# Parsed data.
dict-revised.json.bz2:
	wget http://kcwu.csie.org/~kcwu/moedict/dict-revised.json.bz2 -O $@

dict-revised.json: dict-revised.json.bz2
	bunzip2 -k $^
	# The below line fail, need to investigate
	#wget https://github.com/g0v/moedict-data/raw/master/dict-revised.json

dict-revised.sqlite3.bz2:
	wget http://kcwu.csie.org/~kcwu/moedict/dict-revised.sqlite3.bz2 -O $@

dict-revised.sqlite3: dict-revised.sqlite3.bz2
	bunzip2 -k $^

# Convert to unicode.
dict-revised.unicode.json: json2unicode.pl dict-revised.json
	perl ./json2unicode.pl > $@

# stardict part.
moedict.tab.txt: dict-revised.sqlite3
	dpkg -l python-jinja2 || sudo apt-get install python-jinja2
	python ./moe2dict.py $^ > $@

moedict.xml: dict-revised.unicode.json
	python moe2stardict/moe2dictxml.py $^ > $@

# xml format is not working.
#moedict.ifo: moedict.xml
#	/usr/lib/stardict-tools/stardict-text2bin $^ $@

moedict.tab.ifo: moedict.tab.txt
	dpkg -l stardict-tools || sudo apt-get install stardict-tools
	/usr/lib/stardict-tools/tabfile $^ && echo "use 'make install' to install generated dictionary."

moedict.tar.gz: moedict.tab.ifo moedict.tab.idx moedict.tab.dict.dz
	tar czf $@ $^

tarball: moedict.tar.gz

clean:
	rm -f moedict.idx moedict.ifo moedict.dict.dz moedict.xml dict-revised.unicode.json

install: moedict.tab.ifo
	mkdir -p ~/.stardict/dic/stardict-moedict-2.4.2
	cp moedict.tab.ifo moedict.tab.idx moedict.tab.dict.dz ~/.stardict/dic/stardict-moedict-2.4.2

uninstall:
	rm -rf ~/.stardict/dic/stardict-moedict-2.4.2
