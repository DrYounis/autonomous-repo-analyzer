# Autonomous Repo Analyzer 🤖

> **AI-powered GitHub repository revenue analysis as a SaaS product**

Instantly analyze any GitHub repository for revenue potential. Get monetization strategies, AI trend insights, and a clear path to generating income from your code.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/autonomous-repo-analyzer)

**Live Demo**: [your-deployment-url.railway.app](https://your-deployment-url.railway.app)

---

## 💰 Revenue Potential

| Plan | Price | Repos/month |
|------|-------|-------------|
| Starter | $49/mo | 10 |
| Professional | $99/mo | 50 |
| Agency | $299/mo | Unlimited |

**Target**: 100 users = **$9,900 MRR**

---

## 🏗️ Architecture

```
autonomous-system/
├── api/
│   ├── main.py          ← FastAPI backend + Stripe
│   └── requirements.txt
├── dashboard/
│   └── index.html       ← Premium SaaS UI
├── revenue_analyzer.py  ← Core AI analysis engine
├── trend_tracker.py     ← AI trend intelligence
├── github_manager.py    ← GitHub integration
├── email_reporter.py    ← Email reports
├── autonomous_workflow.py ← Orchestration
├── railway.json         ← Deploy config
├── Procfile             ← Process config
└── .env.example         ← Environment variables
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/DrYounis/autonomous-repo-analyzer
cd autonomous-repo-analyzer
pip install -r api/requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your keys:
# - GITHUB_TOKEN
# - STRIPE_SECRET_KEY
# - STRIPE_WEBHOOK_SECRET
# - STRIPE_STARTER_PRICE_ID
# - STRIPE_PRO_PRICE_ID
# - STRIPE_AGENCY_PRICE_ID
```

### 3. Run Locally

```bash
cd api
uvicorn main:app --reload --port 8000
# Open http://localhost:8000
```

---

## 🔑 Stripe Setup

1. Create a [Stripe account](https://stripe.com)
2. Create 3 products with monthly prices:
   - Starter: $49/month
   - Professional: $99/month
   - Agency: $299/month
3. Copy the Price IDs into your `.env`
4. Set up webhook endpoint: `POST /webhook`
   - Events: `checkout.session.completed`, `customer.subscription.deleted`

---

## 🚂 Deploy to Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard
```

Or click: [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

---

## 🌐 API Reference

### `POST /analyze`
Analyze a repository for revenue potential.

**Headers**: `X-API-Key: your_api_key`

**Body**:
```json
{
  "github_url": "https://github.com/username/repo",
  "github_token": "optional_for_private_repos"
}
```

**Response**:
```json
{
  "repo": "my-project",
  "total_score": 72.5,
  "revenue_potential": "High",
  "estimated_value": 45000,
  "scores": {
    "market_demand": 85,
    "monetization_ready": 60,
    "tech_stack_modern": 90,
    "deployment_ready": 75,
    "user_traction": 40,
    "code_quality": 80,
    "strategic_value": 70
  },
  "monetization_strategies": ["Add Stripe integration", "..."],
  "next_steps": ["Deploy to Vercel", "..."],
  "ai_recommendations": [...]
}
```

### `GET /history`
Get your analysis history.

### `GET /plans`
Get available pricing plans.

### `POST /checkout`
Create a Stripe checkout session.

---

## 🔒 Security

- API key authentication on all protected routes
- Stripe webhook signature verification
- Rate limiting via subscription quotas
- No sensitive data stored (repos cloned to temp dirs)

---

## 📊 Scoring Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Market Demand | 25% | Tech stack popularity, AI/SaaS signals |
| Monetization Ready | 20% | Existing payment code, billing setup |
| Modern Tech Stack | 15% | Next.js, React, FastAPI, etc. |
| Deployment Ready | 15% | Docker, CI/CD, cloud configs |
| User Traction | 10% | Stars, forks, issues |
| Code Quality | 10% | Tests, documentation, structure |
| Strategic Value | 5% | Unique positioning, market fit |

---

## 🗺️ Roadmap

- [x] Core revenue analysis engine
- [x] FastAPI SaaS backend
- [x] Stripe subscription billing
- [x] Premium dashboard UI
- [ ] Supabase persistent storage
- [ ] Email delivery of API keys (SendGrid)
- [ ] GitHub OAuth login
- [ ] Batch analysis (multiple repos)
- [ ] Slack/Discord notifications
- [ ] White-label reports (PDF)

---

## 📄 License

MIT — built by [DrYounis](https://github.com/DrYounis)
