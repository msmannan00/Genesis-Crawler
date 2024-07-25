#!/bin/bash

tor_instances=1
SCRIPT_DIR=$(dirname "$(realpath "$0")")

stop_all_containers() {
    docker stop $(docker ps -aq)
    docker rm $(docker ps -aq)
}

remove_docker_networks() {
    docker network prune -f
}

generate_main_docker_compose() {
    {
        echo "version: '3.8'"
        echo "services:"
        echo "  force-attach:"
        echo "    image: bash"
        echo "    command: tail -f /dev/null"
        echo "  api:"
        echo "    build:"
        echo "      context: $SCRIPT_DIR"
        echo "      dockerfile: $SCRIPT_DIR/dockerFiles/api_docker"
        echo "    ports:"
        echo "      - '8000:8000'"
        echo "    depends_on:"
        echo "      - mongo"
        echo "      - redis_server"
        for ((i=1; i<=tor_instances; i++)); do
            echo "      - 'tor-extend-$i'"
        done
        echo "    environment:"
        echo "      - S_TOR_INSTANCE_COUNT=$tor_instances"
        echo "      - TOR_INSTANCES=$tor_instances"  # Added line
        echo "    deploy:"
        echo "      resources:"
        echo "        limits:"
        echo "          memory: 50G"
        echo "    restart: always"
        echo "    volumes:"
        echo "      - $SCRIPT_DIR/app/:/app"
        echo "    ulimits:"
        echo "      nproc: 65535"
        echo "      nofile:"
        echo "        soft: 26677"
        echo "        hard: 46677"
        echo "    networks:"
        echo "      backend:"
        echo "        ipv4_address: 172.0.0.2"
        echo "  redis_server:"
        echo "    image: redis"
        echo "    logging:"
        echo "      driver: none"
        echo "    command: redis-server --requirepass killprg1"
        echo "    restart: always"
        echo "    networks:"
        echo "      backend:"
        echo "        ipv4_address: 172.0.0.3"
        echo "  mongo:"
        echo "    image: 'mongocamp/mongodb:5.0.9'"
        echo "    container_name: mongo-db"
        echo "    command: mongod --quiet --logpath /dev/null"
        echo "    logging:"
        echo "      driver: none"
        echo "    volumes:"
        echo "      - $SCRIPT_DIR/data/db:/data/db"
        echo "    ports:"
        echo "      - '27017:27017'"
        echo "    restart: always"
        echo "    networks:"
        echo "      backend:"
        echo "        ipv4_address: 172.0.0.4"
        echo "networks:"
        echo "  backend:"
        echo "    driver: bridge"
        echo "    ipam:"
        echo "      driver: default"
        echo "      config:"
        echo "        - subnet: 172.0.0.0/24"
    } > docker-compose.yml
}

generate_tor_docker_compose() {
    {
        echo "version: '3.8'"
        echo "services:"
        for ((i=1; i<=tor_instances; i++)); do
            puid=$((20000 + 2 * i))
            pgid=$((20001 + 2 * i))
            port1=$((9180 + 2 * i))
            port2=$((9181 + 2 * i))
            ipv4_address=$(printf '172.0.0.%d' $((4 + i)))

            echo "  tor-extend-$i:"
            echo "    container_name: tor_instance_$i"
            echo "    image: barneybuffet/tor:latest"
            echo "    volumes:"
            echo "      - ~/Documents/docker/tor_test:/tor$i"
            echo "    ports:"
            echo "      - '$port1:$port1'"
            echo "      - '$port2:$port2'"
            echo "    environment:"
            echo "      PUID: '$puid'"
            echo "      PGID: '$pgid'"
            echo "      TOR_CONFIG_OVERWRITE: 'true'"
            echo "      TOR_LOG_CONFIG: 'true'"
            echo "      TOR_PROXYL: 'true'"
            echo "      TOR_PROXY_PORT: '0.0.0.0:$port1'"
            echo "      TOR_CONTROL_PORT: '0.0.0.0:$port2'"
            echo "      TOR_PROXY_SOCKET: 'true'"
            echo "      TOR_PROXY_ACCEPT: 'accept 172.0.0.0/24,accept 127.0.0.1,accept 10.0.0.0/8,accept 172.16.0.0/12,accept 192.168.0.0/16'"
            echo "      TOR_CONTROL: 'true'"
            echo "      TOR_CONTROL_SOCKET: 'true'"
            echo "      TOR_CONTROL_PASSWORD: 'Imammehdi@00'"
            echo "      TOR_CONTROL_COOKIE: 'true'"
            echo "      TOR_RELAY: 'false'"
            echo "    networks:"
            echo "      backend:"
            echo "        ipv4_address: $ipv4_address"
        done
        echo "networks:"
        echo "  backend:"
        echo "    ipam:"
        echo "      config:"
        echo "        - subnet: 172.0.0.0/24"
    } > docker-compose.tor.yml
}

run_docker_composes() {
    docker-compose -f docker-compose.yml -f docker-compose.tor.yml up
}

restart_tor_services() {
    while true; do
        if ! docker info > /dev/null 2>&1; then
            echo "Docker is not running. Exiting..."
            exit 1
        fi

        sleep 600
        echo "Restarting Tor services..."
        docker-compose -f docker-compose.tor.yml restart
    done
}

stop_all_containers
remove_docker_networks
generate_main_docker_compose
generate_tor_docker_compose
restart_tor_services &
run_docker_composes
