web: bin/upgrade && PYTHONUNBUFFERED=1 bin/web --addr=:${PORT} --debug
worker: bin/upgrade && PYTHONUNBUFFERED=1 bin/worker --no-debug -n 4 -l ${LOG_LEVEL}
static: node_modules/.bin/webpack -d --watch
