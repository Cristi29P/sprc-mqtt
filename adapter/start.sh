#!/bin/sh

check_service() {
    service=$1
    port=$2
    while ! nc -z "$service" "$port" 2>/dev/null; do
        sleep 1
    done
}

check_service "sprc3_broker" 1883
check_service "sprc3_influxdb" 8086

python3 -u adapter.py