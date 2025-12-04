#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Starting Django Task Manager with AI       ║${NC}"
echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Stop any existing containers
echo -e "${YELLOW}Stopping any existing containers...${NC}"
docker-compose down 2>/dev/null

echo ""
echo -e "${BLUE}Starting all services...${NC}"
echo "  - PostgreSQL database"
echo "  - Ollama AI service"
echo "  - Django backend"
echo ""

# Start services
docker-compose up -d

# Wait a moment for services to initialize
echo ""
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 3

# Check service status
echo ""
echo -e "${BLUE}Service Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Application Started!             ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 API:${NC}           http://localhost:8000/api/tasks/"
echo -e "${BLUE}👤 Admin Panel:${NC}  http://localhost:8000/admin"
echo -e "${BLUE}   Username:${NC}     admin"
echo -e "${BLUE}   Password:${NC}     admin"
echo ""

# Check if Ollama model is downloaded
echo -e "${YELLOW}Checking Ollama AI model...${NC}"
MODEL_STATUS=$(docker exec ollama_service ollama list 2>/dev/null | grep llama3.2)

if [ -z "$MODEL_STATUS" ]; then
    echo -e "${YELLOW}⏳ Ollama model (llama3.2) is still downloading...${NC}"
    echo -e "${YELLOW}   This takes ~10-15 minutes on first startup${NC}"
    echo ""
    echo -e "${BLUE}Monitor progress:${NC} docker-compose logs -f ollama"
    echo ""
    echo -e "${YELLOW}⚠️  AI subtask generation will not work until download completes${NC}"
else
    echo -e "${GREEN}✓ Ollama model ready!${NC}"
    echo -e "${GREEN}✓ AI subtask generation is enabled${NC}"
fi

echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs:           docker-compose logs -f"
echo "  View backend logs:   docker-compose logs -f backend"
echo "  Stop services:       docker-compose down"
echo "  Restart:             ./start.sh"
echo ""
echo -e "${BLUE}Test the API:${NC}"
echo "  ./test_api.sh"
echo ""
