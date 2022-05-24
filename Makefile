develop: develop-javascript develop-python

develop-javascript:
	yarn install

develop-python:
	pip install --upgrade pip setuptools wheel
	pip install -e ".[test,pre-commit]"

mac-install-postgres-96:
	# .envrc adds /usr/local/opt/postgresql@9.6/bin/ to PATH.
	# (the old Cellar path stuff is needed for older homebrews/macos)
	brew install --build-from-source postgresql@9.6.rb

upgrade:
	@echo "--> Creating default 'freight' database"
	createdb -E utf-8 freight || true
	@echo "--> Running migrations"
	bin/upgrade

test: test-python test-javascript

test-javascript:
	@echo "--> Running javascript tests"
	yarn run test
	@echo ""

test-python:
	@echo "--> Running Python tests"
	pytest
	@echo ""

docker:
	docker build --pull --rm -t freight .
