#!/bin/bash

set -a
. ./.env
set +a

if curl --output /dev/null --silent --head --fail "$S_SERVER"; then
    echo "Server $S_SERVER is running."
else
    echo "Error: Server $S_SERVER is not reachable. Exiting."
    exit 1
fi

if [ "$1" == "build" ]; then
    docker-compose build --no-cache
    docker-compose up -d
    docker system prune -a --volumes -f
else
    docker-compose up -d
fi
