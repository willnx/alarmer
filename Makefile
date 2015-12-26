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
	-find . -name "*.pyc" -exec rm {} +
	-rm -rf build
	-rm -rf alarmer.egg-info
	-rm -rf dist

build: clean
	if ! test -f $(BUILD_NUM_FILE); then echo 1 > $(BUILD_NUM_FILE); fi
	echo $(NEW_BUILD_NUM) > $(BUILD_NUM_FILE)
  $(PYTHON) setup.py bdist_wheel

install: build
	$(PIP) install dist/*.whl

test: install
	nosestest --with-coverage --package='alarmer'
