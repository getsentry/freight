develop: update-submodules setup-git
	@echo "--> Installing dependencies"
	npm install
	pip install -e .
	pip install "file://`pwd`#egg=freight[test]"

setup-git:
	@echo "--> Installing git hooks"
	git config branch.autosetuprebase always
	cd .git/hooks && ln -sf ../../hooks/* ./
	@echo ""

upgrade:
	@echo "--> Creating default 'freight' database"
	createdb -E utf-8 freight || true
	@echo "--> Running migrations"
	bin/upgrade

update-submodules:
	@echo "--> Updating git submodules"
	git submodule init
	git submodule update
	@echo ""

test: develop lint-python test-python validate-heroku test-javascript

test-javascript:
	@echo "--> Running javascript tests"
	npm run test
	@echo ""

test-python:
	@echo "--> Running Python tests"
	bin/test
	@echo ""

lint-python:
	@echo "--> Linting Python files"
	bin/lint
	@echo ""

validate-heroku:
	@echo "--> Validating app.json"
	npm run validate-app.json
