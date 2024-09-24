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

DOWNLOAD_URL="http://localhost:8080/model/toxic_model"
DEST_DIR="app/raw/toxic_model"
TEMP_ZIP="app/raw/toxic_model.zip"

mkdir -p $DEST_DIR

download_and_extract() {
    echo "Attempting to download $DOWNLOAD_URL..."

    if [ -z "$(ls -A $DEST_DIR)" ]; then
        echo "Toxic model folder is empty. Proceeding with download."

        if curl --output /dev/null --silent --head --fail "$DOWNLOAD_URL"; then
            echo "Downloading file..."
            curl -# -L "$DOWNLOAD_URL" -o "$TEMP_ZIP" || {
                echo "Error: Failed to download the model file."
                exit 1
            }
        else
            echo "Error: Model file URL is not reachable."
            exit 1
        fi

        echo "Extracting toxic_model.zip..."
        unzip -q "$TEMP_ZIP" -d "$DEST_DIR" || {
            echo "Error: Failed to extract toxic_model.zip."
            exit 1
        }

        echo "Removing the zip file..."
        rm "$TEMP_ZIP"

        echo "Download and extraction complete."
    else
        echo "Toxic model folder is not empty. Skipping download."
    fi
}

remove_services() {
    read -p "Are you sure you want to remove all services? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down --volumes
        docker-compose rm -f
    else
        echo "Skipping service removal."
        exit 1
    fi
}

if [ "$1" == "build" ]; then
    remove_services
    download_and_extract
    docker-compose build --no-cache
    docker-compose up -d
    sleep 5
    docker exec -d -it trusted-crawler-main celery -A crawler.crawler_services.crawler_services.celery_manager worker -Q unique_crawler_queue --loglevel=DEBUG
else
    docker-compose down
    download_and_extract
    docker-compose up -d
    sleep 5
    docker exec -d -it trusted-crawler-main celery -A crawler.crawler_services.crawler_services.celery_manager worker -Q unique_crawler_queue --loglevel=DEBUG
fi

