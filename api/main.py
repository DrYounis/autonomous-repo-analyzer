"""
Autonomous Repo Analyzer - FastAPI Backend
SaaS API for AI-powered repository revenue analysis
"""
import os
import sys
import json
import time
import secrets
import tempfile
import subprocess
import stripe
import requests
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

# ── Service startup time tracking ────────────────────────────────────────────
_service_start_time: float = time.time()


@app.get("/health")
async def health():
    """Health check with startup grace period. Does NOT call external services."""
    elapsed = time.time() - _service_start_time
    if elapsed < 5:  # 5-second startup grace period
        return JSONResponse(
            status_code=503,
            content={"status": "starting", "message": f"Service starting ({elapsed:.1f}s)"},
        )
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": f"{elapsed:.1f}s",
        "service": "autonomous-repo-analyzer",
    }

@app.get("/plans")
async def get_plans():
    """Return available pricing plans"""
    return {"plans": PLANS}

@app.post("/analyze")
async def analyze_repository(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(check_quota),
):
    """
    Analyze a GitHub repository for revenue potential.
    Returns scoring across 7 dimensions + monetization strategies.
    """
    github_url = request.github_url.strip().rstrip("/")

    # Extract repo name from URL
    parts = github_url.split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")
    repo_name = parts[-1].replace(".git", "")

    try:
        analyzer = RevenueAnalyzer()
        trend_tracker = TrendTracker()

        # Build minimal repo_info dict from URL
        repo_info = {
            "name": repo_name,
            "url": github_url,
            "stargazers_count": 0,
            "forks_count": 0,
            "open_issues_count": 0,
            "description": "",
        }

        # Use a temp directory for cloning
        with tempfile.TemporaryDirectory() as tmpdir:
            clone_path = Path(tmpdir) / repo_name
            token = request.github_token or os.getenv("GITHUB_TOKEN", "")
            clone_url = github_url
            if token:
                # Inject token into URL
                clone_url = github_url.replace("https://", f"https://{token}@")

            result = subprocess.run(
                ["git", "clone", "--depth=1", clone_url, str(clone_path)],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not clone repository. Make sure it's public or provide a token."
                )

            analysis = analyzer.analyze_repository(repo_info, clone_path)
            trends = trend_tracker.get_latest_trends()
            recommendations = trend_tracker.generate_implementation_recommendations(analysis)

        # Increment usage counter
        user["analyses_this_month"] = user.get("analyses_this_month", 0) + 1

        # Store result
        api_key = user["api_key"]
        if api_key not in analyses_db:
            analyses_db[api_key] = []
        analyses_db[api_key].append({
            "repo": repo_name,
            "url": github_url,
            "score": analysis["total_score"],
            "potential": analysis["revenue_potential"],
            "analyzed_at": datetime.utcnow().isoformat(),
        })

        return {
            "repo": repo_name,
            "url": github_url,
            "total_score": analysis["total_score"],
            "revenue_potential": analysis["revenue_potential"],
            "estimated_value": analysis["estimated_value"],
            "scores": analysis["scores"],
            "monetization_strategies": analysis["monetization_strategies"],
            "next_steps": analysis["next_steps"],
            "ai_recommendations": recommendations[:3],
            "trending_tech": trends.get("frameworks", [])[:5],
            "analyzed_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/history")
async def get_history(user: dict = Depends(get_current_user)):
    """Get analysis history for the current user"""
    api_key = user["api_key"]
    return {
        "analyses": analyses_db.get(api_key, []),
        "total": len(analyses_db.get(api_key, [])),
        "quota_used": user.get("analyses_this_month", 0),
        "quota_limit": PLANS.get(user.get("plan", "starter"), PLANS["starter"])["repos_per_month"],
    }


@app.post("/checkout")
async def create_checkout(request: CheckoutRequest):
    """Create a Stripe checkout session"""
    plan = request.plan.lower()
    if plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")

    plan_info = PLANS[plan]
    price_id = plan_info["price_id"]

    if not price_id:
        raise HTTPException(status_code=500, detail="Stripe price ID not configured")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=request.email,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=os.getenv("BASE_URL", "http://localhost:8000") + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.getenv("BASE_URL", "http://localhost:8000") + "/#pricing",
            metadata={"plan": plan, "email": request.email},
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhook")
async def stripe_webhook(request_body: bytes, stripe_signature: str = Header(None)):
    """Handle Stripe webhook events"""
    try:
        event = stripe.Webhook.construct_event(
            request_body, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session.get("customer_email") or session.get("metadata", {}).get("email", "")
        plan = session.get("metadata", {}).get("plan", "starter")

        # Create API key for new user
        api_key = f"ara_{secrets.token_urlsafe(32)}"
        users_db[api_key] = {
            "email": email,
            "plan": plan,
            "api_key": api_key,
            "created_at": datetime.utcnow().isoformat(),
            "analyses_this_month": 0,
            "stripe_customer_id": session.get("customer"),
        }
        logger.info(f"New user registered: {email} | Plan: {plan}")
        # In production: send API key via email (SendGrid)

    elif event["type"] == "customer.subscription.deleted":
        # Handle cancellation — mark user as inactive
        logger.warning(f"Subscription cancelled: {event['data']['object'].get('id', 'unknown')}")

    return {"received": True}


@app.get("/success")
async def payment_success(session_id: str):
    """Post-payment success page"""
    return HTMLResponse("""
    <html>
    <head><title>Payment Successful</title>
    <style>body{font-family:sans-serif;text-align:center;padding:80px;background:#0a0a1a;color:white;}
    h1{color:#7c3aed;} a{color:#7c3aed;}</style></head>
    <body>
    <h1>🎉 Welcome to Autonomous Repo Analyzer!</h1>
    <p>Your subscription is active. Check your email for your API key.</p>
    <p><a href="/">Go to Dashboard →</a></p>
    </body></html>
    """)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
