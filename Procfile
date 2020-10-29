web: bin/start-pgbouncer gunicorn "homework_fml:create_app()"
worker: rq worker -c worker_config -u $REDIS_URL $REDIS_QUEUE_NAME