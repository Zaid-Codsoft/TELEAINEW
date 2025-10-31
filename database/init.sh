#!/bin/bash

# Tele-AI Database Initialization Script
# This script sets up the PostgreSQL database with schema and seed data

set -e

echo "=========================================="
echo "Tele-AI Database Initialization"
echo "=========================================="
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ Environment variables loaded from .env"
else
    echo "⚠ No .env file found. Using default values or create .env from .env.example"
    cp .env.example .env
    echo "✓ Created .env from .env.example. Please review and update if needed."
fi

echo ""
echo "Database Configuration:"
echo "  Database: ${POSTGRES_DB:-teleai_db}"
echo "  User: ${POSTGRES_USER:-teleai_user}"
echo "  Port: ${POSTGRES_PORT:-5432}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Start the database
echo "Starting PostgreSQL container..."
docker-compose up -d postgres

echo "Waiting for PostgreSQL to be ready..."
sleep 10

# Check if PostgreSQL is ready
until docker exec teleai_postgres pg_isready -U ${POSTGRES_USER:-teleai_user} -d ${POSTGRES_DB:-teleai_db} > /dev/null 2>&1; do
    echo "  Waiting for PostgreSQL..."
    sleep 2
done

echo "✓ PostgreSQL is ready!"
echo ""

# Run schema and seed data (will be auto-loaded by docker-entrypoint-initdb.d)
echo "Database schema and seed data will be automatically loaded on first startup."
echo ""

# Start PgAdmin (optional)
echo "Starting PgAdmin..."
docker-compose up -d pgadmin

echo ""
echo "=========================================="
echo "✅ Database initialization complete!"
echo "=========================================="
echo ""
echo "Database Connection:"
echo "  Host: localhost"
echo "  Port: ${POSTGRES_PORT:-5432}"
echo "  Database: ${POSTGRES_DB:-teleai_db}"
echo "  User: ${POSTGRES_USER:-teleai_user}"
echo "  Password: ${POSTGRES_PASSWORD:-<see .env file>}"
echo ""
echo "PgAdmin Web Interface:"
echo "  URL: http://localhost:${PGADMIN_PORT:-5050}"
echo "  Email: ${PGADMIN_EMAIL:-admin@teleai.com}"
echo "  Password: ${PGADMIN_PASSWORD:-<see .env file>}"
echo ""
echo "Connection String:"
echo "  ${DATABASE_URL:-postgresql://teleai_user:password@localhost:5432/teleai_db}"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f postgres"
echo ""
echo "To stop the database:"
echo "  docker-compose down"
echo ""
echo "To stop and remove all data:"
echo "  docker-compose down -v"
echo ""

