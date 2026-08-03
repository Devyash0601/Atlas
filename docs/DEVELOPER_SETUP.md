# Developer Environment Setup Guide

## System Requirements
- **OS**: macOS (Apple Silicon M1/M2/M3 recommended) or Linux.
- **Python**: Python 3.13+
- **Node.js**: Node 20+
- **Container Runtime**: Docker & Docker Compose

## Quick Setup Steps

```bash
# 1. Clone repository
cd Atlas

# 2. Run automated setup script
./scripts/setup.sh

# 3. Start full environment via Makefile
make dev
```

The API will be available at `http://localhost:8000` and the frontend dashboard at `http://localhost:3000`.
