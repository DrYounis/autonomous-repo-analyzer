#!/usr/bin/env python3
"""
Daily Scheduler - Automated Daily Execution
Run this script via cron to execute the autonomous workflow daily
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import os


def run_daily_workflow():
    """Execute the daily autonomous workflow"""
    
    script_dir = Path(__file__).parent
    workflow_script = script_dir / "autonomous_workflow.py"
    
    print(f"\n{'='*80}")
    print(f"🕐 Daily Workflow Scheduler - {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    if not workflow_script.exists():
        print(f"❌ Workflow script not found: {workflow_script}")
        return 1
    
    try:
        # Run the autonomous workflow
        result = subprocess.run(
            [sys.executable, str(workflow_script)],
            cwd=script_dir,
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Daily workflow completed successfully")
            return 0
        else:
            print(f"\n❌ Workflow failed with exit code: {result.returncode}")
            return result.returncode
            
    except Exception as e:
        print(f"\n❌ Error running workflow: {e}")
        return 1


def setup_cron():
    """Print instructions for setting up cron job"""
    
    script_path = Path(__file__).absolute()
    python_path = sys.executable
    
    print("\n" + "="*80)
    print("⏰ CRON JOB SETUP INSTRUCTIONS")
    print("="*80 + "\n")
    
    print("To run this workflow automatically every day, add this to your crontab:\n")
    
    # Run at 9 AM every day
    cron_line = f"0 9 * * * {python_path} {script_path} >> /tmp/autonomous_workflow.log 2>&1"
    
    print(f"  {cron_line}\n")
    
    print("Steps:")
    print("  1. Open crontab editor:")
    print("     crontab -e\n")
    print("  2. Add the line above")
    print("  3. Save and exit\n")
    
    print("This will run the workflow daily at 9:00 AM")
    print("Logs will be saved to: /tmp/autonomous_workflow.log\n")
    
    print("Alternative schedules:")
    print("  • Every 6 hours:  0 */6 * * *")
    print("  • Twice daily:    0 9,21 * * *")
    print("  • Every weekday:  0 9 * * 1-5")
    print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Workflow Scheduler')
    parser.add_argument('--setup-cron', action='store_true', help='Show cron setup instructions')
    parser.add_argument('--run-now', action='store_true', help='Run workflow immediately')
    
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron()
        return 0
    elif args.run_now:
        return run_daily_workflow()
    else:
        # Default: run the workflow (for cron execution)
        return run_daily_workflow()


if __name__ == "__main__":
    sys.exit(main())
