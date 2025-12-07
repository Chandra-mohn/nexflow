#!/bin/bash
# Check status of Nexflow Docker services
#
# Usage:
#   ./status.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DOCKER_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              NEXFLOW DOCKER ENVIRONMENT STATUS               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Container status
echo "CONTAINER STATUS:"
echo "─────────────────"
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || docker-compose ps

echo ""
echo "SERVICE ENDPOINTS:"
echo "──────────────────"

check_endpoint() {
    local name=$1
    local url=$2
    local port=$3

    if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -q "200\|204"; then
        echo -e "  ${GREEN}✓${NC} $name: $url"
    elif nc -z localhost "$port" 2>/dev/null; then
        echo -e "  ${YELLOW}~${NC} $name: localhost:$port (port open, HTTP not responding)"
    else
        echo -e "  ${RED}✗${NC} $name: localhost:$port (not available)"
    fi
}

check_endpoint "Kafka"           "http://localhost:9093" 9093
check_endpoint "Schema Registry" "http://localhost:8081/subjects" 8081
check_endpoint "Kafka Connect"   "http://localhost:8083/connectors" 8083
check_endpoint "Kafka UI"        "http://localhost:8085" 8085
check_endpoint "MongoDB"         "http://localhost:27017" 27017
check_endpoint "Flink UI"        "http://localhost:8084" 8084
check_endpoint "Spark UI"        "http://localhost:8080" 8080

echo ""
echo "KAFKA CONNECT STATUS:"
echo "─────────────────────"
if curl -s http://localhost:8083/connectors > /dev/null 2>&1; then
    connectors=$(curl -s http://localhost:8083/connectors)
    if [ "$connectors" = "[]" ]; then
        echo "  No connectors deployed"
    else
        echo "  Connectors: $connectors"
        for conn in $(echo "$connectors" | jq -r '.[]' 2>/dev/null); do
            status=$(curl -s "http://localhost:8083/connectors/$conn/status" | jq -r '.connector.state' 2>/dev/null)
            if [ "$status" = "RUNNING" ]; then
                echo -e "    ${GREEN}✓${NC} $conn: $status"
            else
                echo -e "    ${RED}✗${NC} $conn: $status"
            fi
        done
    fi
else
    echo "  Kafka Connect not available"
fi

echo ""
echo "RESOURCE USAGE:"
echo "───────────────"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | grep nexflow || echo "  No containers running"
