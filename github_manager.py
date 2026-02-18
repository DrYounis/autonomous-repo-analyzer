"""
GitHub Manager - Repository Discovery and Management
"""
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime


class GitHubManager:
    """Manages GitHub repository operations"""
    
    def __init__(self, workspace_root: str = os.environ.get("WORKSPACE_ROOT", "/tmp/workspace")):
        self.workspace_root = Path(workspace_root)
        self.repos_cache_file = self.workspace_root / ".github_repos_cache.json"
        
    def is_authenticated(self) -> bool:
        """Check if GitHub CLI is authenticated"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def authenticate(self) -> bool:
        """Guide user through GitHub authentication"""
        if self.is_authenticated():
            print("✅ Already authenticated with GitHub")
            return True
        
        print("\n🔐 GitHub Authentication Required")
        print("Please run: gh auth login")
        print("Then follow the prompts to authenticate.\n")
        return False
    
    def list_repositories(self, force_refresh: bool = False) -> List[Dict]:
        """
        List all repositories accessible to the authenticated user
        
        Args:
            force_refresh: Force refresh from GitHub API instead of using cache
            
        Returns:
            List of repository dictionaries with metadata
        """
        # Check cache first
        if not force_refresh and self.repos_cache_file.exists():
            try:
                with open(self.repos_cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Cache valid for 24 hours
                    cache_time = datetime.fromisoformat(cache_data['timestamp'])
                    if (datetime.now() - cache_time).total_seconds() < 86400:
                        print(f"📦 Using cached repository list ({len(cache_data['repos'])} repos)")
                        return cache_data['repos']
            except Exception as e:
                print(f"⚠️  Cache read error: {e}")
        
        if not self.is_authenticated():
            print("❌ Not authenticated. Please run: gh auth login")
            return []
        
        print("🔍 Fetching repositories from GitHub...")
        
        try:
            # Get all repos (owned + collaborated)
            result = subprocess.run(
                ["gh", "repo", "list", "--json", "name,owner,description,url,isPrivate,updatedAt,primaryLanguage,stargazerCount"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ Error fetching repos: {result.stderr}")
                return []
            
            repos = json.loads(result.stdout)
            
            # Also get repos from organizations
            org_result = subprocess.run(
                ["gh", "repo", "list", "--source", "--json", "name,owner,description,url,isPrivate,updatedAt,primaryLanguage,stargazerCount"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if org_result.returncode == 0:
                org_repos = json.loads(org_result.stdout)
                repos.extend(org_repos)
            
            # Remove duplicates
            unique_repos = {repo['url']: repo for repo in repos}.values()
            repos = list(unique_repos)
            
            # Cache the results
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'repos': repos
            }
            
            with open(self.repos_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"✅ Found {len(repos)} repositories")
            return repos
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def clone_repository(self, repo_url: str, target_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Clone a repository to the workspace
        
        Args:
            repo_url: GitHub repository URL
            target_dir: Optional target directory (default: workspace_root/repos/)
            
        Returns:
            Path to cloned repository or None if failed
        """
        if target_dir is None:
            target_dir = self.workspace_root / "repos"
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract repo name from URL
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        repo_path = target_dir / repo_name
        
        # Check if already cloned
        if repo_path.exists() and (repo_path / ".git").exists():
            print(f"📁 Repository already cloned: {repo_name}")
            # Pull latest changes
            try:
                subprocess.run(
                    ["git", "pull"],
                    cwd=repo_path,
                    capture_output=True,
                    timeout=30
                )
                print(f"✅ Updated {repo_name}")
            except Exception as e:
                print(f"⚠️  Could not update {repo_name}: {e}")
            return repo_path
        
        print(f"📥 Cloning {repo_name}...")
        
        try:
            result = subprocess.run(
                ["gh", "repo", "clone", repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"✅ Cloned {repo_name}")
                return repo_path
            else:
                print(f"❌ Failed to clone {repo_name}: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error cloning {repo_name}: {e}")
            return None
    
    def get_repository_info(self, repo_path: Path) -> Dict:
        """
        Get detailed information about a repository
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Dictionary with repository metadata
        """
        info = {
            'path': str(repo_path),
            'name': repo_path.name,
            'exists': repo_path.exists(),
            'is_git': (repo_path / ".git").exists(),
        }
        
        if not info['is_git']:
            return info
        
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            info['branch'] = result.stdout.strip()
            
            # Get last commit
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%an|%ae|%s|%ci"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split('|')
                if len(parts) == 5:
                    info['last_commit'] = {
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'message': parts[3],
                        'date': parts[4]
                    }
            
            # Get file count
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                info['file_count'] = len(result.stdout.strip().split('\n'))
            
            # Check for common files
            info['has_readme'] = (repo_path / "README.md").exists()
            info['has_package_json'] = (repo_path / "package.json").exists()
            info['has_requirements_txt'] = (repo_path / "requirements.txt").exists()
            info['has_dockerfile'] = (repo_path / "Dockerfile").exists()
            
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def commit_and_push(self, repo_path: Path, message: str, files: List[str] = None) -> bool:
        """
        Commit and push changes to a repository
        
        Args:
            repo_path: Path to the repository
            message: Commit message
            files: List of files to commit (None = all changes)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add files
            if files:
                for file in files:
                    subprocess.run(
                        ["git", "add", file],
                        cwd=repo_path,
                        timeout=10
                    )
            else:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=repo_path,
                    timeout=10
                )
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("ℹ️  No changes to commit")
                    return True
                else:
                    print(f"❌ Commit failed: {result.stderr}")
                    return False
            
            # Push
            result = subprocess.run(
                ["git", "push"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ Pushed changes to {repo_path.name}")
                return True
            else:
                print(f"❌ Push failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


if __name__ == "__main__":
    # Test the GitHub manager
    manager = GitHubManager()
    
    if manager.authenticate():
        repos = manager.list_repositories()
        print(f"\n📊 Repository Summary:")
        print(f"Total repositories: {len(repos)}")
        
        if repos:
            print("\nTop 5 repositories:")
            for i, repo in enumerate(repos[:5], 1):
                print(f"{i}. {repo['name']} - {repo.get('description', 'No description')}")
