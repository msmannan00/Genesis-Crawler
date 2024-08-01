#!/bin/bash

filename="filtered_url.txt"

if [ -f "$filename" ]; then
    > "$filename"
else
    touch "$filename"
fi

if [ -n "$(docker ps -aq)" ]; then
    docker stop $(docker ps -aq)
    docker rm $(docker ps -aq)
fi

if [ -n "$(docker images -q)" ]; then
    docker rmi $(docker images -q)
fi

if [ -n "$(docker volume ls -q)" ]; then
    docker volume rm $(docker volume ls -q)
fi

network_ids=$(docker network ls | grep "bridge\|none\|host" -v | awk '{print $1}')
if [ -n "$network_ids" ]; then
    docker network rm $network_ids
fi
