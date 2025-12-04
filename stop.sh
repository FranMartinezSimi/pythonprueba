#!/bin/bash

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}Stopping all services...${NC}"
docker-compose down

echo ""
echo -e "${GREEN}✓ All services stopped${NC}"
echo ""
echo "To start again, run: ./start.sh"
