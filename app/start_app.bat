#!/bin/bash

if [ "$1" == 'api' ]; then
    echo "Launching Genesis Crawler"
    python3 main.py

elif [ "$1" == 'genbot_service' ]; then
    echo "Launching Genbot Worker"
    celery -A crawler.crawler_instance.genbot_service.genbot_controller worker --concurrency=100 --pool=gevent --loglevel=info -Q genbot_queue
else
    echo "Must provide a valid argument"
    exit 1
fi
