#!/bin/bash

if [ "$1" == "start_app" ]; then
  python3 main.py --command invoke_celery_crawler
fi
