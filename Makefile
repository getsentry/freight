develop: update-submodules setup-git
	@echo "--> Installing dependencies"
	pip install -e .
	pip install "file://`pwd`#egg=ds[test]"

setup-git:
	@echo "--> Installing git hooks"
	git config branch.autosetuprebase always
	cd .git/hooks && ln -sf ../../hooks/* ./
	@echo ""

update-submodules:
	@echo "--> Updating git submodules"
	git submodule init
	git submodule update
	@echo ""

test: develop lint-python test-python validate-heroku

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
