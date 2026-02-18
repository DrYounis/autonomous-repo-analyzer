# 🚀 Quick Setup Guide

Get your autonomous system running in 10 minutes!

## Step 1: GitHub Authentication (2 minutes)

```bash
# Install GitHub CLI if needed
brew install gh

# Authenticate
gh auth login
```

Follow the prompts:
1. Choose "GitHub.com"
2. Choose "HTTPS"
3. Authenticate via browser
4. Grant repository access

## Step 2: Install Dependencies (1 minute)

```bash
cd "/Volumes/Elements/AG/ai deveopers/autonomous-system"
pip install -r requirements.txt
```

## Step 3: Configure Email (3 minutes)

### Option A: SendGrid (Recommended)

1. Go to [sendgrid.com/free](https://sendgrid.com/free)
2. Sign up for free account
3. Create API key: Settings → API Keys → Create API Key
4. Copy the key

```bash
cp .env.example .env
```

Edit `.env`:
```
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your_actual_key_here
SENDER_EMAIL=autonomous@yourdomain.com
```

### Option B: Skip Email (Reports saved to files)

Just run without configuring email. Reports will be saved to `reports/` directory.

## Step 4: Test Run (2 minutes)

```bash
# Dry run (no changes made)
python autonomous_workflow.py --dry-run
```

You should see:
- ✅ GitHub authentication successful
- 📂 Repositories discovered
- 💰 Revenue analysis complete
- 📧 Report generated

## Step 5: Set Up Daily Automation (2 minutes)

```bash
# Get cron instructions
python daily_scheduler.py --setup-cron

# Add to crontab
crontab -e
```

Add this line (runs daily at 9 AM):
```
0 9 * * * /usr/bin/python3 "/Volumes/Elements/AG/ai deveopers/autonomous-system/daily_scheduler.py" >> /tmp/autonomous.log 2>&1
```

## ✅ You're Done!

The system will now:
- Run automatically every day at 9 AM
- Analyze all your GitHub repositories
- Prioritize revenue-generating projects
- Track AI trends
- Send daily reports to op.younis@gmail.com

## 🎯 Next Steps

1. Check your email tomorrow morning for the first report
2. Review the priority queue: `python autonomous_workflow.py --status`
3. Implement suggested improvements on high-value repos
4. Monitor progress via daily emails

## 🚨 Troubleshooting

**"gh: command not found"**
```bash
brew install gh
```

**"Not authenticated"**
```bash
gh auth login
```

**"Email not sent"**
- Check `.env` configuration
- Or skip email - reports saved to `reports/`

**"No repositories found"**
- Make sure `gh auth login` completed successfully
- Check you have repository access

---

**Need help?** Check the full [README.md](README.md) for detailed documentation.
