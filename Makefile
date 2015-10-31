#
#
#
#

PIP=`which pip`
PYTHON=`which python`

BUILD_NUM_FILE='build-number.txt'
NEW_BUILD_NUM=`expr \`cat build-number.txt\` + 1`

clean:
	-$(PIP) uninstall -y alarmer
	-rm *.pyc
	-rm -rf build
	-rm -rf alarmer.egg-info
	-rm -rf dist

install: clean
	python setup.py install

build: clean
	if ! test -f $(BUILD_NUM_FILE); then echo 1 > $(BUILD_NUM_FILE); fi
	echo $(NEW_BUILD_NUM) > $(BUILD_NUM_FILE)
