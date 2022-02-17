#!/bin/bash

# Run migrations
alembic upgrade head

# Start Server
uvicorn src.main:app --host 0.0.0.0 --port 5001 --debug --reload-dir /app --log-level debug