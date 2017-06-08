web: bin/upgrade && PYTHONUNBUFFERED=1 bin/web --no-debug --addr=:${PORT}
worker: bin/upgrade && PYTHONUNBUFFERED=1 bin/worker --no-debug -n 4 -l ${LOG_LEVEL}
