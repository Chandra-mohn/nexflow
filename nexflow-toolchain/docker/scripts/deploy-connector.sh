#!/bin/bash
# Deploy Kafka Connect connectors
#
# Usage:
#   ./deploy-connector.sh                    # Deploy all connectors
#   ./deploy-connector.sh mongodb-sink       # Deploy specific connector

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"
CONNECTORS_DIR="$DOCKER_DIR/connectors"

CONNECT_URL="${KAFKA_CONNECT_URL:-http://localhost:8083}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

wait_for_connect() {
    log_info "Waiting for Kafka Connect to be ready..."
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$CONNECT_URL/" > /dev/null 2>&1; then
            log_info "Kafka Connect is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    log_error "Kafka Connect is not available at $CONNECT_URL"
    return 1
}

deploy_connector() {
    local config_file=$1
    local connector_name=$(basename "$config_file" .json)

    log_info "Deploying connector: $connector_name"

    # Check if connector exists
    if curl -s "$CONNECT_URL/connectors/$connector_name" | grep -q "\"name\":"; then
        log_warn "Connector $connector_name exists, updating..."
        curl -s -X PUT \
            -H "Content-Type: application/json" \
            -d @"$config_file" \
            "$CONNECT_URL/connectors/$connector_name/config" | jq .
    else
        log_info "Creating new connector: $connector_name"
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -d @"$config_file" \
            "$CONNECT_URL/connectors" | jq .
    fi

    # Check status
    sleep 2
    local status=$(curl -s "$CONNECT_URL/connectors/$connector_name/status" | jq -r '.connector.state')
    if [ "$status" = "RUNNING" ]; then
        log_info "Connector $connector_name is RUNNING"
    else
        log_warn "Connector $connector_name status: $status"
    fi
}

list_connectors() {
    log_info "Current connectors:"
    curl -s "$CONNECT_URL/connectors" | jq .
}

# Main
wait_for_connect

if [ $# -eq 0 ]; then
    # Deploy all connectors
    log_info "Deploying all connectors from $CONNECTORS_DIR"
    for config_file in "$CONNECTORS_DIR"/*.json; do
        if [ -f "$config_file" ]; then
            deploy_connector "$config_file"
        fi
    done
else
    # Deploy specific connector
    config_file="$CONNECTORS_DIR/$1.json"
    if [ -f "$config_file" ]; then
        deploy_connector "$config_file"
    else
        log_error "Connector config not found: $config_file"
        exit 1
    fi
fi

echo ""
list_connectors
