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

test: test-python test-javascript

lint: lint-python

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

format: format-python

format-python:
	@echo "--> Formatting Python files"
	python -m black . bin/run-task bin/load-mocks bin/shell bin/ssh-connect bin/web bin/worker bin/load-mocks
	@echo ""

docker:
	docker build --pull --rm -t freight .
