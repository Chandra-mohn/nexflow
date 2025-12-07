#!/bin/bash
# Create Kafka topics for Nexflow
#
# Usage:
#   ./create-topics.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Topic configuration
PARTITIONS=3
REPLICATION=1

# Define topics
TOPICS=(
    "transactions"
    "enriched-transactions"
    "alerts"
    "fraud-scores"
    "velocity-metrics"
    "dlq-mongodb-sink"
)

log_info "Creating Kafka topics..."

for topic in "${TOPICS[@]}"; do
    log_info "Creating topic: $topic"
    docker exec nexflow-kafka kafka-topics \
        --bootstrap-server localhost:9092 \
        --create \
        --if-not-exists \
        --topic "$topic" \
        --partitions $PARTITIONS \
        --replication-factor $REPLICATION \
        2>/dev/null || true
done

log_info "Listing all topics:"
docker exec nexflow-kafka kafka-topics \
    --bootstrap-server localhost:9092 \
    --list
