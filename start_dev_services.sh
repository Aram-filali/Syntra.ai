#!/bin/bash

# Syntra.ai Development Server Startup Script
# Starts all required services for development
# 
# Usage: bash start_dev_services.sh
# Or in separate terminals:
#   - Terminal 1: redis-server
#   - Terminal 2: uvicorn app.main:app --reload (from backend/)
#   - Terminal 3: npm run dev (from frontend/)
#   - Terminal 4: celery -A app.tasks.celery_app worker --loglevel=info -Q meetings
#   - Terminal 5: celery -A app.tasks.celery_app beat --loglevel=info

echo "================================"
echo "Syntra.ai Development Environment"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Redis
if ! command -v redis-server &> /dev/null; then
    echo -e "${RED}❌ Redis not installed${NC}"
    echo "Install Redis:"
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-server"
    echo "  Or use Docker: docker run -d -p 6379:6379 redis:latest"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not installed${NC}"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites met${NC}"
echo ""

# Start Redis
echo "🚀 Starting Redis..."
redis-server --daemonize yes
sleep 2

# Verify Redis is running
if redis-cli ping | grep -q PONG; then
    echo -e "${GREEN}✅ Redis running${NC}"
else
    echo -e "${RED}❌ Redis failed to start${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📌 Services ready! Use separate terminals:${NC}"
echo ""
echo "Terminal 1 (FastAPI Backend):"
echo "  cd backend && uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 (React Frontend):"
echo "  cd frontend && npm run dev"
echo ""
echo "Terminal 3 (Celery Worker):"
echo "  cd backend && celery -A app.tasks.celery_app worker --loglevel=info -Q meetings"
echo ""
echo "Terminal 4 (Celery Beat - Scheduler):"
echo "  cd backend && celery -A app.tasks.celery_app beat --loglevel=info"
echo ""
echo "Terminal 5 (Celery Flower - Monitoring):"
echo "  pip install flower && celery -A app.tasks.celery_app flower"
echo "  Then visit: http://localhost:5555"
echo ""
echo -e "${GREEN}Redis is running in background (daemonize mode)${NC}"
echo ""
echo "To stop Redis:"
echo "  redis-cli shutdown"
echo ""
