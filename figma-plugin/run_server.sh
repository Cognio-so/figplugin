#!/bin/bash

# Navigate to backend directory for env file
cd backend
# Load environment variables and export them
set -a
source .env
set +a
# Go back to parent directory to run the server
cd ..
# Start the server with proper module path
python -m uvicorn backend.main:app --reload --port 8000