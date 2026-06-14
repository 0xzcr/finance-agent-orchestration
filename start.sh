#!/bin/bash

# ============================================================
# Finance Agent Orchestration — Full System Launcher
# ============================================================
# Starts both the FastAPI backend and React frontend.
# Usage: ./start.sh
# ============================================================

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║     📈 Finance Agent Orchestration              ║"
echo "║     CrewAI + Cerebras + Zerodha                 ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# --- Cleanup on exit ---
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null && echo -e "${GREEN}✓ Backend stopped${NC}"
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null && echo -e "${GREEN}✓ Frontend stopped${NC}"
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM

# --- Check prerequisites ---
echo -e "${CYAN}[1/5] Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ python3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ node not found. Please install Node.js 18+${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm not found. Please install npm${NC}"
    exit 1
fi

echo -e "${GREEN}✓ python3, node, npm found${NC}"

# --- Backend setup ---
echo ""
echo -e "${CYAN}[2/5] Setting up backend...${NC}"

if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv "$BACKEND_DIR/venv"
fi

source "$BACKEND_DIR/venv/bin/activate"

echo "  Installing backend dependencies..."
pip install -q -r "$BACKEND_DIR/requirements.txt"

# Install finance_agents package in the venv
pip install -q -e "$ROOT_DIR/finance_agents"

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# --- Check .env ---
echo ""
echo -e "${CYAN}[3/5] Checking configuration...${NC}"

if [ ! -f "$BACKEND_DIR/.env" ]; then
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    echo -e "${YELLOW}⚠ Created backend/.env from template — please add your API keys${NC}"
fi

# Source .env to check keys
set -a
source "$BACKEND_DIR/.env"
set +a

if [ "$CEREBRAS_API_KEY" = "your_cerebras_api_key_here" ] || [ -z "$CEREBRAS_API_KEY" ]; then
    echo -e "${YELLOW}⚠ CEREBRAS_API_KEY not set in backend/.env${NC}"
    echo -e "  Get a free key at: ${CYAN}https://cloud.cerebras.ai${NC}"
else
    echo -e "${GREEN}✓ Cerebras API key configured${NC}"
fi

if [ -z "$KITE_API_KEY" ] || [ "$KITE_API_KEY" = "your_kite_api_key_here" ]; then
    echo -e "${YELLOW}⚠ Zerodha not configured (optional — Alpha Vantage will be used)${NC}"
else
    echo -e "${GREEN}✓ Zerodha API key configured${NC}"
fi

# --- Frontend setup ---
echo ""
echo -e "${CYAN}[4/5] Setting up frontend...${NC}"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "  Installing frontend dependencies..."
    (cd "$FRONTEND_DIR" && npm install --silent)
fi

echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# --- Start services ---
echo ""
echo -e "${CYAN}[5/5] Starting services...${NC}"
echo ""

# Start backend
echo -e "  Starting backend on ${GREEN}http://localhost:8000${NC}..."
(cd "$BACKEND_DIR" && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
BACKEND_PID=$!

# Wait for backend to be ready
echo "  Waiting for backend..."
for i in {1..15}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Backend running${NC}"
else
    echo -e "  ${YELLOW}⚠ Backend may still be starting...${NC}"
fi

# Start frontend
echo -e "  Starting frontend on ${GREEN}http://localhost:5173${NC}..."
(cd "$FRONTEND_DIR" && npm run dev -- --host) &
FRONTEND_PID=$!

sleep 3

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ System is running!                           ║${NC}"
echo -e "${GREEN}║                                                  ║${NC}"
echo -e "${GREEN}║  Frontend: http://localhost:5173                 ║${NC}"
echo -e "${GREEN}║  Backend:  http://localhost:8000                 ║${NC}"
echo -e "${GREEN}║  API Docs: http://localhost:8000/docs            ║${NC}"
echo -e "${GREEN}║                                                  ║${NC}"
echo -e "${GREEN}║  Press Ctrl+C to stop all services               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# Wait for processes
wait
