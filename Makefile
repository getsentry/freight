develop:
	@echo "--> Installing dependencies"
	yarn install
	pip install -e ".[test,pre-commit]"

mac-install-postgres-96:
	# .envrc adds /usr/local/opt/postgresql@9.6/bin/ to PATH.
	# (the old Cellar path stuff is needed for older homebrews/macos)
	brew install --build-from-source postgresql@9.6.rb
	# TODO: postgresql service.
	#       Also I think, I need redis.

upgrade:
	@echo "--> Creating default 'freight' database"
	createdb -E utf-8 freight || true
	@echo "--> Running migrations"
	bin/upgrade

test: test-python test-javascript

lint: lint-python

test-javascript:
	@echo "--> Running javascript tests"
	yarn run test
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
	# TODO: pre-commit
	python -m black . bin/run-task bin/load-mocks bin/shell bin/ssh-connect bin/web bin/worker bin/load-mocks
	@echo ""

docker:
	docker build --pull --rm -t freight .
