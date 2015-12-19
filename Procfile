web: bin/upgrade && PYTHONUNBUFFERED=1 bin/web --no-debug --addr=:${PORT}
worker: bin/upgrade && PYTHONUNBUFFERED=1 bin/worker -n 4 -l ${LOG_LEVEL}--no-debug
