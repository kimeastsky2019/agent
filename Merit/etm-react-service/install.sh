#!/bin/bash

echo "======================================"
echo "ETM React - Installation"
echo "======================================"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}[1/4] Cloning repositories...${NC}"

# Clone ETEngine
if [ ! -d "etengine" ]; then
    echo "Cloning ETEngine..."
    git clone https://github.com/quintel/etengine.git
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to clone ETEngine${NC}"
        exit 1
    fi
else
    echo "ETEngine directory already exists."
fi

# Clone ETSource
if [ ! -d "etsource" ]; then
    echo "Cloning ETSource..."
    git clone https://github.com/quintel/etsource.git
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to clone ETSource${NC}"
        exit 1
    fi
else
    echo "ETSource directory already exists."
fi

echo -e "${GREEN}Repository cloning complete!${NC}"

echo -e "${YELLOW}[2/4] Creating environment configuration...${NC}"

# ETEngine environment configuration
cat > etengine/.env <<EOF
RAILS_ENV=development
DATABASE_URL=postgresql://etm:etm_password@postgres:5432/etengine_development
REDIS_URL=redis://redis:6379/0
ETSOURCE_PATH=/app/etsource
SECRET_KEY_BASE=development_secret_key_base_change_in_production
EOF

echo -e "${GREEN}Environment configuration complete!${NC}"

echo -e "${YELLOW}[3/4] Building Docker images... (this may take a while)${NC}"

docker-compose build

if [ $? -ne 0 ]; then
    echo -e "${RED}Docker image build failed${NC}"
    exit 1
fi

echo -e "${GREEN}Docker image build complete!${NC}"

echo -e "${YELLOW}[4/4] Starting services...${NC}"

docker-compose up -d postgres redis

echo "Waiting for database to be ready... (30 seconds)"
sleep 30

docker-compose up -d etengine

echo "Waiting for ETEngine initialization... (30 seconds)"
sleep 30

docker-compose up -d react-frontend nginx

echo ""
echo -e "${GREEN}======================================"
echo "Installation Complete!"
echo "======================================${NC}"
echo ""
echo "Service Access Information:"
echo "  - Main Application: http://localhost"
echo "  - React Frontend (Direct): http://localhost:3000"
echo "  - ETEngine API: http://localhost:3001"
echo ""
echo "Service Management Commands:"
echo "  - Start: docker-compose up -d"
echo "  - Stop: docker-compose down"
echo "  - View logs: docker-compose logs -f [service_name]"
echo "  - Check status: docker-compose ps"
echo ""
echo -e "${YELLOW}Note: The React app may take a minute to compile on first startup.${NC}"
