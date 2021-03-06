# Portions of Makefile are from https://github.com/dustalov/watset.

export LANG=en_US.UTF-8
export MAVEN_OPTS=-Dmaven.test.skip=true -Dmaven.javadoc.skip=true

export P ?= 0.8
export T ?= 10
export E ?= log
export N ?= 1
export H ?= tf

all: egos clusters babelnet-clusters arrange evaluate

deps: chinese-whispers babelnet-extract pip

egos:
	rm -rf "$(CURDIR)/lmdb"
	./00-convert.py
	./11-ego-batch.sh

clusters:
	./22-edges-batch.sh
	rm -fv 20-edges.txt
	./24-prune-batch.sh
	rm -fv 22-prune-raw.txt
	./25-pos.py
	rm -fv 24-prune.txt
	./26-cw.sh
	python -m lmdb -S 20480 -e "$(CURDIR)/lmdb" drop hypernyms
	./30-isas.py

arrange:
	./arrange.sh

evaluate:
	./evaluate.sh

chinese-whispers: chinese-whispers-master.zip
	rm -rf chinese-whispers-master
	unzip chinese-whispers-master.zip
	mv chinese-whispers-master chinese-whispers
	mvn -f chinese-whispers/pom.xml -T $$(nproc) package

chinese-whispers-master.zip:
	curl -sLo 'chinese-whispers-master.zip' 'https://github.com/uhh-lt/chinese-whispers/archive/master.zip'

export BABELNET=3.7

babelnet-extract: babelnet-extract.zip BabelNet-API-3.7.zip
	ls BabelNet-API-$$BABELNET.zip >/dev/null 2>&1
	rm -rf BabelNet-API-$$BABELNET
	unzip BabelNet-API-$$BABELNET.zip
	rm -rf babelnet-extract
	unzip babelnet-extract.zip
	mv babelnet-extract-f7e1cf9dacc84b5a6c03d928780d5777e910934a babelnet-extract
	mvn install:install-file -Dfile=BabelNet-API-$$BABELNET/lib/jltutils-2.2.jar -DgroupId=it.uniroma1.lcl.jlt -DartifactId=jltutils -Dversion=2.2 -Dpackaging=jar
	unzip -p BabelNet-API-$$BABELNET/babelnet-api-$$BABELNET.jar META-INF/maven/it.uniroma1.lcl.babelnet/babelnet-api/pom.xml | grep -vP '<(scope|systemPath)>' >BabelNet-API-$$BABELNET/babelnet-api-$$BABELNET.pom
	mvn install:install-file -Dfile=BabelNet-API-$$BABELNET/babelnet-api-$$BABELNET.jar -DpomFile=BabelNet-API-$$BABELNET/babelnet-api-$$BABELNET.pom
	ln -sfT $(CURDIR)/BabelNet-API-$$BABELNET/config $(CURDIR)/babelnet-extract/config
	ln -sfT $(CURDIR)/BabelNet-API-$$BABELNET/resources $(CURDIR)/babelnet-extract/resources
	mvn -f babelnet-extract/pom.xml package

babelnet-clusters:
	./51-clusters.sh

BabelNet-API-3.7.zip:
	wget 'https://github.com/nlpub/babelnet-extract/releases/download/bn37/BabelNet-API-3.7.zip'

babelnet-extract.zip:
	wget -O babelnet-extract.zip "https://github.com/nlpub/babelnet-extract/archive/f7e1cf9dacc84b5a6c03d928780d5777e910934a.zip"

pip:
	pip install -r requirements.txt

ddt.tsv: ddt.tsv.gz
	gunzip ddt.tsv.gz

ddt.tsv.gz:
	wget -O 'ddt.tsv.gz' 'http://panchenko.me/data/joint/ddt/ddt-mwe-45g-8m-thr-agressive2-cw-e0-N200-n200-minsize5-isas-cmb-nopos-closure.csv.gz'

clean:
	find . -maxdepth 1 -name '*.txt' ! \( -name 'requirements.txt' -o -name 'params.py.txt' \) -type f -exec rm -fv {} +
	rm -fv *.csv *.log
	rm -rf "$(CURDIR)/lmdb"
