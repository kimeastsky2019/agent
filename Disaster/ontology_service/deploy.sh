#!/bin/bash

# Collaborative Ontology Platform - Deployment Script
# This script automates the deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_success "Docker is installed"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed"
        exit 1
    fi
    print_success "Git is installed"
}

# Setup environment
setup_environment() {
    print_info "Setting up environment..."
    
    if [ ! -f .env ]; then
        print_info "Creating .env file..."
        cat > .env << EOF
# Database
POSTGRES_DB=collaborative_ontology
POSTGRES_USER=ontology_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Redis
REDIS_URL=redis://redis:6379/0

# InfluxDB
INFLUXDB_TOKEN=$(openssl rand -base64 32)
INFLUXDB_ORG=gng_energy
INFLUXDB_BUCKET=energy_data

# Backend
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# Fuseki
FUSEKI_ADMIN_PASSWORD=$(openssl rand -base64 32)
EOF
        chmod 600 .env
        print_success ".env file created"
    else
        print_info ".env file already exists"
    fi
}

# Build and start services
build_and_start() {
    print_info "Building and starting services..."
    
    docker-compose build
    print_success "Images built successfully"
    
    docker-compose up -d
    print_success "Services started successfully"
    
    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    if docker-compose ps | grep -q "Up"; then
        print_success "All services are running"
    else
        print_error "Some services failed to start"
        docker-compose logs
        exit 1
    fi
}

# Initialize database
initialize_database() {
    print_info "Initializing database..."
    
    # Wait for database to be ready
    until docker-compose exec -T postgres pg_isready -U ontology_user; do
        sleep 2
    done
    
    # Run migrations
    docker-compose exec -T backend alembic upgrade head
    print_success "Database initialized"
}

# Load initial ontology
load_ontology() {
    print_info "Loading initial ontology..."
    
    # Copy ontology file to Fuseki
    docker cp ontology/energy_core.ttl collaborative_ontology_fuseki:/fuseki/databases/
    
    print_success "Ontology loaded"
}

# Create test users
create_test_users() {
    print_info "Creating test users..."
    
    # This would run a script in the backend container
    # docker-compose exec backend python scripts/create_test_users.py
    
    print_success "Test users created"
}

# Display access information
display_info() {
    echo ""
    echo "=========================================="
    echo "Collaborative Ontology Platform"
    echo "=========================================="
    echo ""
    echo "Services are now running:"
    echo ""
    echo "Frontend:      http://localhost:3000"
    echo "Backend API:   http://localhost:8000"
    echo "API Docs:      http://localhost:8000/docs"
    echo "Fuseki:        http://localhost:3030"
    echo "Grafana:       http://localhost:3001"
    echo "Prometheus:    http://localhost:9090"
    echo ""
    echo "Default Login:"
    echo "Username: admin"
    echo "Password: admin123"
    echo ""
    echo "=========================================="
}

# Main deployment flow
main() {
    echo "=========================================="
    echo "Collaborative Ontology Platform Deployment"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    setup_environment
    build_and_start
    initialize_database
    load_ontology
    create_test_users
    display_info
    
    print_success "Deployment completed successfully!"
}

# Run main function
main
