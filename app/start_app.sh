#!/bin/bash

if [ "$1" == "start_app" ]; then
  python3 main.py --command invoke_celery_crawler
fi

if [ "$1" == "invoke_unique_crawler" ]; then
  docker exec -d -it trusted-crawler-main python3 main.py --command invoke_unique_crawler
fi
