web: bin/upgrade && bin/web --no-debug --addr=:${PORT}
worker: bin/upgrade && bin/worker -l ${LOG_LEVEL} -c 8 --maxtasksperchild=1
