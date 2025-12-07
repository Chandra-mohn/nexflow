#!/bin/bash
# Nexflow Docker Environment - Stop Script
#
# Usage:
#   ./stop.sh          # Stop all services (preserve data)
#   ./stop.sh clean    # Stop all services and remove volumes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DOCKER_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

case "${1:-stop}" in
    stop)
        log_info "Stopping all Nexflow services..."
        docker-compose down
        log_info "All services stopped. Data volumes preserved."
        ;;

    clean)
        log_warn "Stopping all services and removing volumes..."
        read -p "This will delete all data. Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            log_info "All services stopped and volumes removed."
        else
            log_info "Aborted."
        fi
        ;;

    *)
        echo "Usage: $0 {stop|clean}"
        echo ""
        echo "  stop   - Stop services, preserve data"
        echo "  clean  - Stop services and delete all data"
        exit 1
        ;;
esac
