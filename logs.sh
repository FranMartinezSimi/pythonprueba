#!/bin/bash

# Colors
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Showing logs for all services...${NC}"
echo "Press Ctrl+C to stop"
echo ""

docker-compose logs -f
