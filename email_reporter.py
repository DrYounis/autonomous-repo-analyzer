"""
Email Reporter - Automated Daily Progress Reports
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import json


class EmailReporter:
    """Sends automated daily progress reports"""
    
    def __init__(self, recipient_email: str = "op.younis@gmail.com"):
        self.recipient_email = recipient_email
        self.sender_email = os.getenv("SENDER_EMAIL", "autonomous.dev@system.local")
        
        # Support multiple email providers
        self.email_provider = os.getenv("EMAIL_PROVIDER", "sendgrid")
        
        # SendGrid
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        
        # Gmail SMTP
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        
        # Mailgun
        self.mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        self.mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    
    def send_via_sendgrid(self, subject: str, html_body: str, text_body: str) -> bool:
        """Send email via SendGrid API"""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            
            message = Mail(
                from_email=Email(self.sender_email),
                to_emails=To(self.recipient_email),
                subject=subject,
                plain_text_content=Content("text/plain", text_body),
                html_content=Content("text/html", html_body)
            )
            
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Email sent via SendGrid to {self.recipient_email}")
                return True
            else:
                print(f"❌ SendGrid error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ SendGrid error: {e}")
            return False
    
    def send_via_gmail(self, subject: str, html_body: str, text_body: str) -> bool:
        """Send email via Gmail SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.gmail_password)
                server.send_message(msg)
            
            print(f"✅ Email sent via Gmail to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail error: {e}")
            return False
    
    def send_via_mailgun(self, subject: str, html_body: str, text_body: str) -> bool:
        """Send email via Mailgun API"""
        try:
            import requests
            
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                auth=("api", self.mailgun_api_key),
                data={
                    "from": self.sender_email,
                    "to": [self.recipient_email],
                    "subject": subject,
                    "text": text_body,
                    "html": html_body
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Email sent via Mailgun to {self.recipient_email}")
                return True
            else:
                print(f"❌ Mailgun error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Mailgun error: {e}")
            return False
    
    def send_daily_report(self, report_data: Dict) -> bool:
        """
        Send daily progress report
        
        Args:
            report_data: Dictionary containing report information
            
        Returns:
            True if email sent successfully
        """
        date_str = datetime.now().strftime("%B %d, %Y")
        subject = f"🤖 Daily Development Report - {date_str}"
        
        # Generate email body
        html_body = self._generate_html_report(report_data, date_str)
        text_body = self._generate_text_report(report_data, date_str)
        
        # Try to send via configured provider
        if self.email_provider == "sendgrid" and self.sendgrid_api_key:
            return self.send_via_sendgrid(subject, html_body, text_body)
        elif self.email_provider == "gmail" and self.gmail_password:
            return self.send_via_gmail(subject, html_body, text_body)
        elif self.email_provider == "mailgun" and self.mailgun_api_key:
            return self.send_via_mailgun(subject, html_body, text_body)
        else:
            # Fallback: save to file
            return self._save_to_file(subject, text_body)
    
    def _generate_html_report(self, data: Dict, date_str: str) -> str:
        """Generate HTML email body"""
        
        achievements_html = ""
        for repo in data.get('repositories_worked_on', []):
            achievements_html += f"""
            <li>
                <strong>{repo['name']}</strong>: {repo['work_done']}
                <br><small style="color: #666;">Commits: {repo.get('commits', 0)} | Impact: {repo.get('impact', 'Medium')}</small>
            </li>
            """
        
        opportunities_html = ""
        for opp in data.get('revenue_opportunities', []):
            opportunities_html += f"<li>{opp}</li>"
        
        next_steps_html = ""
        for step in data.get('next_steps', []):
            next_steps_html += f"<li>{step}</li>"
        
        issues_html = ""
        for issue in data.get('issues', []):
            issues_html += f"<li>{issue}</li>"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .section h2 {{ margin-top: 0; color: #667eea; }}
                .metric {{ display: inline-block; background: white; padding: 15px 20px; border-radius: 8px; margin: 10px 10px 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 10px; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🤖 Daily Development Report</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">{date_str}</p>
                </div>
                
                <div class="section">
                    <h2>📊 Summary</h2>
                    <div class="metric">
                        <div class="metric-value">{data.get('repos_worked_on', 0)}</div>
                        <div class="metric-label">Repositories</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{data.get('commits_pushed', 0)}</div>
                        <div class="metric-label">Commits</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${data.get('revenue_impact', 0):,}</div>
                        <div class="metric-label">Est. Revenue Impact</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🚀 Today's Achievements</h2>
                    <ul>{achievements_html if achievements_html else '<li>No work completed today</li>'}</ul>
                </div>
                
                <div class="section">
                    <h2>💰 Revenue Opportunities</h2>
                    <ul>{opportunities_html if opportunities_html else '<li>No new opportunities identified</li>'}</ul>
                </div>
                
                <div class="section">
                    <h2>🔮 Next Steps</h2>
                    <ul>{next_steps_html if next_steps_html else '<li>Planning in progress</li>'}</ul>
                </div>
                
                {f'<div class="section"><h2>⚠️ Issues & Blockers</h2><ul>{issues_html}</ul></div>' if issues_html else ''}
                
                <div class="section">
                    <h2>📈 Metrics</h2>
                    <ul>
                        <li><strong>Total Revenue Potential:</strong> ${data.get('total_revenue_potential', 0):,}</li>
                        <li><strong>Active Projects:</strong> {data.get('active_projects', 0)}</li>
                        <li><strong>Deployment Status:</strong> {data.get('deployment_status', '0%')}</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>Generated by Autonomous Development System</p>
                    <p>Powered by AI • Working with OpenAI-level excellence</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_text_report(self, data: Dict, date_str: str) -> str:
        """Generate plain text email body"""
        
        text = f"""
Daily Development Report - {date_str}

📊 SUMMARY
- Repositories worked on: {data.get('repos_worked_on', 0)}
- Commits pushed: {data.get('commits_pushed', 0)}
- Revenue impact: ${data.get('revenue_impact', 0):,}

🚀 TODAY'S ACHIEVEMENTS
"""
        
        for repo in data.get('repositories_worked_on', []):
            text += f"- {repo['name']}: {repo['work_done']}\n"
        
        text += "\n💰 REVENUE OPPORTUNITIES\n"
        for opp in data.get('revenue_opportunities', []):
            text += f"- {opp}\n"
        
        text += "\n🔮 NEXT STEPS\n"
        for step in data.get('next_steps', []):
            text += f"- {step}\n"
        
        if data.get('issues'):
            text += "\n⚠️ ISSUES & BLOCKERS\n"
            for issue in data.get('issues', []):
                text += f"- {issue}\n"
        
        text += f"""
📈 METRICS
- Total revenue potential: ${data.get('total_revenue_potential', 0):,}
- Active projects: {data.get('active_projects', 0)}
- Deployment status: {data.get('deployment_status', '0%')}

---
Generated by Autonomous Development System
"""
        
        return text
    
    def _save_to_file(self, subject: str, body: str) -> bool:
        """Fallback: save report to file if email fails"""
        try:
            reports_dir = Path(os.environ.get("REPORTS_DIR", "/tmp/autonomous-system/reports"))
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = reports_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(f"{subject}\n\n{body}")
            
            print(f"📄 Report saved to: {filepath}")
            print(f"⚠️  Email not configured. Please set up SendGrid, Gmail, or Mailgun.")
            return True
            
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False


if __name__ == "__main__":
    # Test the email reporter
    reporter = EmailReporter()
    
    test_data = {
        'repos_worked_on': 3,
        'commits_pushed': 12,
        'revenue_impact': 5000,
        'repositories_worked_on': [
            {'name': 'turathna-hub', 'work_done': 'Added payment integration', 'commits': 5, 'impact': 'High'},
            {'name': 'grid-trading-bot', 'work_done': 'Optimized trading algorithm', 'commits': 4, 'impact': 'Medium'},
            {'name': 'volunteer-system', 'work_done': 'Fixed deployment issues', 'commits': 3, 'impact': 'Low'},
        ],
        'revenue_opportunities': [
            'Turathna Hub: Add subscription tier for premium artisans',
            'Grid Bot: Offer managed trading service',
        ],
        'next_steps': [
            'Tomorrow: Implement AI-powered product recommendations for Turathna',
            'This week: Launch Grid Bot SaaS platform',
        ],
        'issues': [],
        'total_revenue_potential': 50000,
        'active_projects': 8,
        'deployment_status': '75%',
    }
    
    reporter.send_daily_report(test_data)
