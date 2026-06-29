from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from backend.memory.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("data", exist_ok=True)
    init_db()
    print("✓ Database ready")
    yield

app = FastAPI(
    title="Agentic AI Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers — done individually so failures are visible
try:
    from backend.api import runs
    app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
    print("✓ runs router OK")
except Exception as e:
    print(f"✗ runs router FAILED: {e}")

try:
    from backend.api import config
    app.include_router(config.router, prefix="/api/config", tags=["config"])
    print("✓ config router OK")
except Exception as e:
    print(f"✗ config router FAILED: {e}")

try:
    from backend.api import hitl
    app.include_router(hitl.router, prefix="/api/hitl", tags=["hitl"])
    print("✓ hitl router OK")
except Exception as e:
    print(f"✗ hitl router FAILED: {e}")
try:
    from backend.api import email as email_api
    app.include_router(email_api.router, prefix="/api/email", tags=["email"])
    print("✓ email router OK")
except Exception as e:
    print(f"✗ email router FAILED: {e}")
try:
    from backend.api import agents as agents_api
    app.include_router(agents_api.router, prefix="/api/agents", tags=["agents"])
    print("✓ agents router OK")
except Exception as e:
    print(f"✗ agents router FAILED: {e}")

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")