"""
Revenue Analyzer - AI-Powered Revenue Potential Analysis
"""
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import subprocess


class RevenueAnalyzer:
    """Analyzes repositories for revenue potential"""
    
    # Revenue scoring weights
    WEIGHTS = {
        'market_demand': 0.25,
        'monetization_ready': 0.20,
        'tech_stack_modern': 0.15,
        'deployment_ready': 0.15,
        'user_traction': 0.10,
        'code_quality': 0.10,
        'strategic_value': 0.05,
    }
    
    # High-value technology indicators
    HIGH_VALUE_TECH = {
        'saas': ['next.js', 'react', 'vue', 'stripe', 'supabase', 'vercel'],
        'ai_ml': ['tensorflow', 'pytorch', 'openai', 'langchain', 'huggingface', 'ollama'],
        'blockchain': ['solidity', 'web3', 'ethereum', 'hardhat'],
        'api': ['fastapi', 'express', 'graphql', 'rest'],
        'mobile': ['react-native', 'flutter', 'swift', 'kotlin'],
        'ecommerce': ['shopify', 'woocommerce', 'stripe', 'paypal'],
    }
    
    # Monetization indicators
    MONETIZATION_SIGNALS = [
        'stripe', 'paypal', 'subscription', 'payment', 'billing',
        'pricing', 'checkout', 'commerce', 'shop', 'marketplace'
    ]
    
    def analyze_repository(self, repo_info: Dict, repo_path: Path) -> Dict:
        """
        Analyze a repository for revenue potential
        
        Args:
            repo_info: Repository metadata from GitHub
            repo_path: Local path to repository
            
        Returns:
            Dictionary with revenue analysis
        """
        analysis = {
            'name': repo_info.get('name', repo_path.name),
            'url': repo_info.get('url', ''),
            'scores': {},
            'total_score': 0,
            'revenue_potential': 'Unknown',
            'monetization_strategies': [],
            'next_steps': [],
            'estimated_value': 0,
        }
        
        # Analyze different aspects
        analysis['scores']['market_demand'] = self._analyze_market_demand(repo_info, repo_path)
        analysis['scores']['monetization_ready'] = self._analyze_monetization_readiness(repo_path)
        analysis['scores']['tech_stack_modern'] = self._analyze_tech_stack(repo_path)
        analysis['scores']['deployment_ready'] = self._analyze_deployment_readiness(repo_path)
        analysis['scores']['user_traction'] = self._analyze_user_traction(repo_info)
        analysis['scores']['code_quality'] = self._analyze_code_quality(repo_path)
        analysis['scores']['strategic_value'] = self._analyze_strategic_value(repo_info, repo_path)
        
        # Calculate weighted total score
        total = sum(
            score * self.WEIGHTS[category]
            for category, score in analysis['scores'].items()
        )
        analysis['total_score'] = round(total, 2)
        
        # Determine revenue potential tier
        if total >= 80:
            analysis['revenue_potential'] = 'Very High'
            analysis['estimated_value'] = 50000
        elif total >= 60:
            analysis['revenue_potential'] = 'High'
            analysis['estimated_value'] = 25000
        elif total >= 40:
            analysis['revenue_potential'] = 'Medium'
            analysis['estimated_value'] = 10000
        elif total >= 20:
            analysis['revenue_potential'] = 'Low'
            analysis['estimated_value'] = 2000
        else:
            analysis['revenue_potential'] = 'Very Low'
            analysis['estimated_value'] = 500
        
        # Generate monetization strategies
        analysis['monetization_strategies'] = self._generate_monetization_strategies(repo_path, analysis)
        
        # Generate next steps
        analysis['next_steps'] = self._generate_next_steps(analysis)
        
        return analysis
    
    def _analyze_market_demand(self, repo_info: Dict, repo_path: Path) -> float:
        """Analyze market demand based on stars, description, and category"""
        score = 0
        
        # GitHub stars
        stars = repo_info.get('stargazerCount', 0)
        if stars > 100:
            score += 40
        elif stars > 50:
            score += 30
        elif stars > 10:
            score += 20
        elif stars > 0:
            score += 10
        
        # Check for trending keywords
        description = (repo_info.get('description', '') or '').lower()
        trending_keywords = ['ai', 'ml', 'saas', 'marketplace', 'automation', 'analytics', 'crypto']
        
        for keyword in trending_keywords:
            if keyword in description:
                score += 10
        
        # Check for README quality
        readme_path = repo_path / "README.md"
        if readme_path.exists():
            try:
                content = readme_path.read_text()
                if len(content) > 1000:  # Detailed README
                    score += 20
                elif len(content) > 200:
                    score += 10
            except:
                pass
        
        return min(score, 100)
    
    def _analyze_monetization_readiness(self, repo_path: Path) -> float:
        """Check if repository has monetization features"""
        score = 0
        
        # Search for monetization-related files and code
        try:
            result = subprocess.run(
                ["git", "grep", "-i", "-l"] + self.MONETIZATION_SIGNALS,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                matches = len(result.stdout.strip().split('\n'))
                score += min(matches * 10, 50)
        except:
            pass
        
        # Check for payment configuration files
        payment_files = ['stripe.config', 'payment.config', '.env.example']
        for file in payment_files:
            if (repo_path / file).exists():
                score += 15
        
        # Check package.json for payment libraries
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                content = package_json.read_text()
                if any(lib in content for lib in ['stripe', '@stripe', 'paypal']):
                    score += 30
            except:
                pass
        
        return min(score, 100)
    
    def _analyze_tech_stack(self, repo_path: Path) -> float:
        """Analyze if using modern, high-value technology"""
        score = 0
        
        # Check package.json
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                content = package_json.read_text().lower()
                
                for category, techs in self.HIGH_VALUE_TECH.items():
                    for tech in techs:
                        if tech in content:
                            score += 10
                            break  # One per category
            except:
                pass
        
        # Check requirements.txt
        requirements = repo_path / "requirements.txt"
        if requirements.exists():
            try:
                content = requirements.read_text().lower()
                
                for category, techs in self.HIGH_VALUE_TECH.items():
                    for tech in techs:
                        if tech in content:
                            score += 10
                            break
            except:
                pass
        
        # Modern framework indicators
        modern_files = ['next.config.js', 'vite.config.js', 'tsconfig.json']
        for file in modern_files:
            if (repo_path / file).exists():
                score += 15
        
        return min(score, 100)
    
    def _analyze_deployment_readiness(self, repo_path: Path) -> float:
        """Check if ready for deployment"""
        score = 0
        
        # Dockerfile
        if (repo_path / "Dockerfile").exists():
            score += 30
        
        # CI/CD
        ci_paths = ['.github/workflows', '.gitlab-ci.yml', 'vercel.json', 'netlify.toml']
        for path in ci_paths:
            if (repo_path / path).exists():
                score += 20
                break
        
        # Environment config
        if (repo_path / ".env.example").exists():
            score += 15
        
        # Build scripts
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                content = json.loads(package_json.read_text())
                if 'build' in content.get('scripts', {}):
                    score += 20
            except:
                pass
        
        # Documentation
        docs_paths = ['docs/', 'DEPLOY.md', 'CONTRIBUTING.md']
        for path in docs_paths:
            if (repo_path / path).exists():
                score += 5
        
        return min(score, 100)
    
    def _analyze_user_traction(self, repo_info: Dict) -> float:
        """Analyze user traction from GitHub metrics"""
        score = 0
        
        stars = repo_info.get('stargazerCount', 0)
        if stars > 1000:
            score += 50
        elif stars > 100:
            score += 30
        elif stars > 10:
            score += 15
        
        # Recent activity
        updated_at = repo_info.get('updatedAt', '')
        if updated_at:
            try:
                from datetime import datetime
                updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_since_update = (datetime.now(updated.tzinfo) - updated).days
                
                if days_since_update < 7:
                    score += 30
                elif days_since_update < 30:
                    score += 20
                elif days_since_update < 90:
                    score += 10
            except:
                pass
        
        return min(score, 100)
    
    def _analyze_code_quality(self, repo_path: Path) -> float:
        """Analyze code quality indicators"""
        score = 50  # Base score
        
        # Tests
        test_dirs = ['tests/', 'test/', '__tests__', 'spec/']
        for test_dir in test_dirs:
            if (repo_path / test_dir).exists():
                score += 20
                break
        
        # Linting config
        lint_files = ['.eslintrc', '.prettierrc', 'pyproject.toml', '.flake8']
        for lint_file in lint_files:
            if (repo_path / lint_file).exists():
                score += 10
                break
        
        # TypeScript
        if (repo_path / "tsconfig.json").exists():
            score += 15
        
        return min(score, 100)
    
    def _analyze_strategic_value(self, repo_info: Dict, repo_path: Path) -> float:
        """Analyze strategic value beyond immediate revenue"""
        score = 50
        
        # Portfolio value
        description = (repo_info.get('description', '') or '').lower()
        strategic_keywords = ['platform', 'framework', 'library', 'tool', 'system']
        
        for keyword in strategic_keywords:
            if keyword in description:
                score += 10
        
        return min(score, 100)
    
    def _generate_monetization_strategies(self, repo_path: Path, analysis: Dict) -> List[str]:
        """Generate monetization strategy recommendations"""
        strategies = []
        
        # Check what type of project it is
        has_frontend = (repo_path / "package.json").exists()
        has_backend = (repo_path / "requirements.txt").exists() or (repo_path / "go.mod").exists()
        
        if analysis['scores']['monetization_ready'] < 30:
            strategies.append("Add Stripe payment integration for premium features")
            strategies.append("Implement subscription tiers (Basic/Pro/Enterprise)")
        
        if has_frontend and analysis['scores']['deployment_ready'] > 50:
            strategies.append("Deploy to Vercel with usage-based pricing")
            strategies.append("Add analytics to track user behavior and conversion")
        
        if has_backend:
            strategies.append("Create API tier with rate limiting for paid plans")
            strategies.append("Offer managed hosting service")
        
        if analysis['scores']['user_traction'] > 60:
            strategies.append("Launch on Product Hunt for visibility")
            strategies.append("Create affiliate program for user referrals")
        
        strategies.append("Add freemium model with generous free tier")
        strategies.append("Create marketplace listing (Shopify/WordPress)")
        
        return strategies[:5]  # Top 5 strategies
    
    def _generate_next_steps(self, analysis: Dict) -> List[str]:
        """Generate actionable next steps"""
        steps = []
        
        if analysis['scores']['deployment_ready'] < 50:
            steps.append("Set up CI/CD pipeline with GitHub Actions")
            steps.append("Create Dockerfile for containerization")
        
        if analysis['scores']['code_quality'] < 60:
            steps.append("Add unit tests to improve reliability")
            steps.append("Set up linting and code formatting")
        
        if analysis['scores']['tech_stack_modern'] < 50:
            steps.append("Modernize dependencies to latest versions")
            steps.append("Consider migrating to TypeScript for better DX")
        
        if analysis['scores']['monetization_ready'] < 40:
            steps.append("Integrate payment processing (Stripe recommended)")
            steps.append("Design pricing tiers and feature gates")
        
        steps.append("Create comprehensive documentation")
        steps.append("Set up error tracking (Sentry/LogRocket)")
        
        return steps[:5]  # Top 5 next steps


if __name__ == "__main__":
    # Test the analyzer
    analyzer = RevenueAnalyzer()
    
    test_repo_info = {
        'name': 'test-saas-app',
        'description': 'AI-powered SaaS platform for automation',
        'stargazerCount': 150,
        'updatedAt': datetime.now().isoformat(),
    }
    
    test_path = Path("/Volumes/Elements/AG/ai deveopers/dual-agent-system")
    
    if test_path.exists():
        analysis = analyzer.analyze_repository(test_repo_info, test_path)
        
        print(f"\n📊 Revenue Analysis for {analysis['name']}")
        print(f"Total Score: {analysis['total_score']}/100")
        print(f"Revenue Potential: {analysis['revenue_potential']}")
        print(f"Estimated Value: ${analysis['estimated_value']:,}")
        print(f"\nTop Monetization Strategies:")
        for i, strategy in enumerate(analysis['monetization_strategies'], 1):
            print(f"{i}. {strategy}")
