#!/bin/bash
# Nexflow Docker Environment - Start Script
#
# Usage:
#   ./start.sh              # Start all services
#   ./start.sh kafka        # Start only Kafka stack (Kafka, Zookeeper, Schema Registry)
#   ./start.sh streaming    # Start Kafka + Flink
#   ./start.sh batch        # Start Kafka + Spark
#   ./start.sh full         # Start everything including UI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DOCKER_DIR"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

wait_for_service() {
    local service=$1
    local max_attempts=${2:-30}
    local attempt=1

    log_info "Waiting for $service to be healthy..."
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps "$service" 2>/dev/null | grep -q "healthy"; then
            log_info "$service is healthy!"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    log_error "$service did not become healthy in time"
    return 1
}

case "${1:-all}" in
    kafka)
        log_info "Starting Kafka stack (Zookeeper, Kafka, Schema Registry)..."
        docker-compose up -d zookeeper kafka schema-registry
        wait_for_service kafka
        wait_for_service schema-registry
        log_info "Kafka stack is ready!"
        log_info "  Kafka: localhost:9093"
        log_info "  Schema Registry: http://localhost:8081"
        ;;

    streaming)
        log_info "Starting streaming stack (Kafka + Flink)..."
        docker-compose up -d zookeeper kafka schema-registry flink-jobmanager flink-taskmanager
        wait_for_service kafka
        wait_for_service flink-jobmanager
        log_info "Streaming stack is ready!"
        log_info "  Kafka: localhost:9093"
        log_info "  Flink UI: http://localhost:8084"
        ;;

    batch)
        log_info "Starting batch stack (Kafka + Spark)..."
        docker-compose up -d zookeeper kafka schema-registry spark-master spark-worker
        wait_for_service kafka
        wait_for_service spark-master
        log_info "Batch stack is ready!"
        log_info "  Kafka: localhost:9093"
        log_info "  Spark UI: http://localhost:8080"
        ;;

    mongodb)
        log_info "Starting MongoDB with Kafka Connect..."
        docker-compose up -d zookeeper kafka schema-registry mongodb kafka-connect
        wait_for_service kafka
        wait_for_service mongodb
        wait_for_service kafka-connect
        log_info "MongoDB stack is ready!"
        log_info "  MongoDB: localhost:27017"
        log_info "  Kafka Connect: http://localhost:8083"
        ;;

    full|all)
        log_info "Starting full Nexflow environment..."
        docker-compose up -d
        wait_for_service kafka
        wait_for_service schema-registry
        wait_for_service mongodb
        wait_for_service flink-jobmanager
        wait_for_service spark-master
        wait_for_service kafka-connect

        log_info "Full environment is ready!"
        echo ""
        echo "Services available:"
        echo "  Kafka:           localhost:9093"
        echo "  Schema Registry: http://localhost:8081"
        echo "  Kafka Connect:   http://localhost:8083"
        echo "  Kafka UI:        http://localhost:8085"
        echo "  MongoDB:         localhost:27017"
        echo "  Flink UI:        http://localhost:8084"
        echo "  Spark UI:        http://localhost:8080"
        ;;

    *)
        echo "Usage: $0 {kafka|streaming|batch|mongodb|full|all}"
        echo ""
        echo "  kafka      - Zookeeper, Kafka, Schema Registry"
        echo "  streaming  - Kafka + Flink"
        echo "  batch      - Kafka + Spark"
        echo "  mongodb    - Kafka + MongoDB + Kafka Connect"
        echo "  full/all   - Everything including Kafka UI"
        exit 1
        ;;
esac
