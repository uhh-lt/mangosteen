# Portions of Makefile are from https://github.com/dustalov/watset.

export LANG=en_US.UTF-8
export MAVEN_OPTS=-Dmaven.test.skip=true -Dmaven.javadoc.skip=true

chinese-whispers: chinese-whispers-master.zip
	rm -rf chinese-whispers-master
	unzip chinese-whispers-master.zip
	mv chinese-whispers-master chinese-whispers
	mvn -f chinese-whispers/pom.xml -T $$(nproc) package

chinese-whispers-master.zip:
	curl -sLo 'chinese-whispers-master.zip' 'https://github.com/uhh-lt/chinese-whispers/archive/master.zip'

export BABELNET=3.7

babelnet-extract: babelnet-extract.zip
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

babelnet-extract.zip:
	wget -O babelnet-extract.zip "https://github.com/nlpub/babelnet-extract/archive/f7e1cf9dacc84b5a6c03d928780d5777e910934a.zip"
