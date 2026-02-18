"""
Autonomous Repo Analyzer - FastAPI Backend
SaaS API for AI-powered repository revenue analysis
"""
import os
import sys
import json
import stripe
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add parent directory to path for existing modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from revenue_analyzer import RevenueAnalyzer
from trend_tracker import TrendTracker

# ── Stripe Setup ──────────────────────────────────────────────────────────────
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# ── Pricing Plans ─────────────────────────────────────────────────────────────
PLANS = {
    "starter": {
        "name": "Starter",
        "price": 49,
        "price_id": os.getenv("STRIPE_STARTER_PRICE_ID", ""),
        "repos_per_month": 10,
        "features": ["10 repo analyses/month", "Revenue scoring", "PDF reports", "Email support"],
    },
    "professional": {
        "name": "Professional",
        "price": 99,
        "price_id": os.getenv("STRIPE_PRO_PRICE_ID", ""),
        "repos_per_month": 50,
        "features": ["50 repo analyses/month", "AI trend insights", "Priority queue", "Slack alerts", "API access"],
    },
    "agency": {
        "name": "Agency",
        "price": 299,
        "price_id": os.getenv("STRIPE_AGENCY_PRICE_ID", ""),
        "repos_per_month": -1,  # unlimited
        "features": ["Unlimited analyses", "White-label reports", "Team seats (5)", "Dedicated support", "Custom integrations"],
    },
}

# ── Simple in-memory DB (replace with Supabase in production) ─────────────────
users_db: Dict[str, dict] = {}
analyses_db: Dict[str, list] = {}

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Autonomous Repo Analyzer API",
    description="API for analyzing repositories and tracking trends",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    logger.info(f"✅ Autonomous System API started at {datetime.now().isoformat()}")
    logger.info(f"Available routes: {[route.path for route in app.routes]}")
    logger.info("Configuration loaded successfully")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ───────────────────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    github_url: str
    github_token: Optional[str] = None

class CheckoutRequest(BaseModel):
    plan: str
    email: str

class WebhookEvent(BaseModel):
    type: str

# ── Auth Helper ───────────────────────────────────────────────────────────────
def get_current_user(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key not in users_db:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return users_db[x_api_key]

def check_quota(user: dict = Depends(get_current_user)):
    plan = user.get("plan", "starter")
    plan_info = PLANS.get(plan, PLANS["starter"])
    limit = plan_info["repos_per_month"]
    used = user.get("analyses_this_month", 0)
    if limit != -1 and used >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly quota exceeded ({used}/{limit}). Upgrade your plan."
        )
    return user

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard"""
    dashboard = Path(__file__).parent.parent / "dashboard" / "index.html"
    if dashboard.exists():
        return FileResponse(dashboard)
    return HTMLResponse("<h1>Autonomous Repo Analyzer API</h1><p>Visit /docs for API documentation.</p>")
