import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Set, Tuple
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Commit import Commit
from github.File import File
from dotenv import load_dotenv
from tqdm import tqdm
from collections import defaultdict

class ForkAnalyzer:
    def __init__(self, github_token: str):
        self.github = Github(github_token)
        
    def get_repository(self, repo_name: str) -> Repository:
        """Get the repository object from GitHub."""
        return self.github.get_repo(repo_name)
    
    def get_forks(self, repo: Repository) -> List[Repository]:
        """Get all forks of the repository."""
        return list(repo.get_forks())
    
    def get_file_changes(self, repo: Repository, original_repo: Repository) -> Dict[str, List[Dict[str, Any]]]:
        """Get all file changes in a fork compared to the original repository."""
        try:
            # Get the default branch of both repositories
            fork_branch = repo.default_branch
            original_branch = original_repo.default_branch
            
            # Get the comparison between the fork and original repo
            comparison = repo.compare(f"{original_repo.owner.login}:{original_branch}", fork_branch)
            
            # Process each file change
            file_changes = defaultdict(list)
            for file in comparison.files:
                change_info = {
                    'filename': file.filename,
                    'status': file.status,
                    'additions': file.additions,
                    'deletions': file.deletions,
                    'changes': file.changes,
                    'patch': file.patch,
                    'commit_sha': comparison.commits[0].sha if comparison.commits else None,
                    'commit_message': comparison.commits[0].commit.message if comparison.commits else None,
                }
                file_changes[file.filename].append(change_info)
            
            return dict(file_changes)
        except Exception as e:
            print(f"Error getting file changes for {repo.full_name}: {str(e)}")
            return {}
    
    def analyze_fork(self, fork: Repository, original_repo: Repository) -> Dict[str, Any]:
        """Analyze a single fork and return metrics."""
        # Get basic metrics
        metrics = {
            'name': fork.full_name,
            'stars': fork.stargazers_count,
            'forks': fork.get_forks().totalCount,
            'open_issues': fork.open_issues_count,
            'last_updated': fork.updated_at,
            'description': fork.description,
            'url': fork.html_url,
        }
        
        # Get commit activity
        try:
            commits = fork.get_commits()
            metrics['commit_count'] = commits.totalCount
            metrics['last_commit'] = commits[0].commit.author.date if commits.totalCount > 0 else None
        except Exception:
            metrics['commit_count'] = 0
            metrics['last_commit'] = None
        
        # Get pull requests
        try:
            pulls = fork.get_pulls(state='all')
            metrics['pull_requests'] = pulls.totalCount
        except Exception:
            metrics['pull_requests'] = 0
        
        # Get file changes
        metrics['file_changes'] = self.get_file_changes(fork, original_repo)
        
        # Calculate activity score
        metrics['activity_score'] = self._calculate_activity_score(metrics)
        
        return metrics
    
    def _calculate_activity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate an activity score based on various metrics."""
        score = 0.0
        
        # Weight different factors
        if metrics['stars'] > 0:
            score += min(metrics['stars'] * 2, 50)  # Cap at 50 points for stars
        
        if metrics['commit_count'] > 0:
            score += min(metrics['commit_count'] * 0.5, 25)  # Cap at 25 points for commits
        
        if metrics['pull_requests'] > 0:
            score += min(metrics['pull_requests'] * 5, 25)  # Cap at 25 points for PRs
        
        # Recent activity bonus
        if metrics['last_commit']:
            now = datetime.now(timezone.utc)
            last_commit = metrics['last_commit']
            # GitHub API dates may be offset-aware (UTC) or naive; normalize for subtraction
            if last_commit.tzinfo is None:
                last_commit = last_commit.replace(tzinfo=timezone.utc)
            days_since_last_commit = (now - last_commit).days
            if days_since_last_commit < 30:
                score += 20  # Bonus for recent activity
        
        return score
    
    def analyze_repository(self, repo_name: str) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        """Analyze all forks of a repository and return sorted results and aggregated changes."""
        print(f"Analyzing repository: {repo_name}")
        
        # Get the original repository
        original_repo = self.get_repository(repo_name)
        
        # Get all forks
        forks = self.get_forks(original_repo)
        print(f"Found {len(forks)} forks")
        
        # Analyze each fork
        results = []
        all_file_changes = defaultdict(list)
        
        for fork in tqdm(forks, desc="Analyzing forks"):
            try:
                metrics = self.analyze_fork(fork, original_repo)
                results.append(metrics)
                
                # Aggregate file changes
                for filename, changes in metrics['file_changes'].items():
                    for change in changes:
                        change['fork_name'] = fork.full_name
                        change['fork_url'] = fork.html_url
                        all_file_changes[filename].append(change)
                
            except Exception as e:
                print(f"Error analyzing fork {fork.full_name}: {str(e)}")
        
        # Sort results by activity score
        results.sort(key=lambda x: x['activity_score'], reverse=True)
        return results, dict(all_file_changes)

def main():
    # Load GitHub token from environment variable
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token in a .env file or environment variable")
        sys.exit(1)
    
    if len(sys.argv) != 2:
        print("Usage: python -m git_updates_checker.analyzers.fork <repository_name>")
        print("Example: python -m git_updates_checker.analyzers.fork octocat/Hello-World")
        sys.exit(1)
    
    repo_name = sys.argv[1]
    analyzer = ForkAnalyzer(github_token)
    
    try:
        results, file_changes = analyzer.analyze_repository(repo_name)
        
        # Print top forks
        print("\nTop 10 Most Active Forks:")
        print("-" * 80)
        for i, result in enumerate(results[:10], 1):
            print(f"\n{i}. {result['name']}")
            print(f"   URL: {result['url']}")
            print(f"   Activity Score: {result['activity_score']:.1f}")
            print(f"   Stars: {result['stars']}")
            print(f"   Commits: {result['commit_count']}")
            print(f"   Pull Requests: {result['pull_requests']}")
            if result['last_commit']:
                print(f"   Last Commit: {result['last_commit']}")
            if result['description']:
                print(f"   Description: {result['description']}")
            print("-" * 80)
        
        # Print file changes summary
        print("\nFile Changes Summary:")
        print("-" * 80)
        for filename, changes in file_changes.items():
            print(f"\nFile: {filename}")
            print(f"Total changes: {len(changes)}")
            
            # Group changes by status
            status_counts = defaultdict(int)
            for change in changes:
                status_counts[change['status']] += 1
            
            print("Change types:")
            for status, count in status_counts.items():
                print(f"  - {status}: {count}")
            
            # Show forks that modified this file
            print("\nModified by forks:")
            for change in changes:
                print(f"  - {change['fork_name']}")
                print(f"    URL: {change['fork_url']}")
                if change['commit_message']:
                    first_line = change['commit_message'].split('\n')[0]
                    print(f"    Commit message: {first_line}")
                print(f"    Changes: +{change['additions']} -{change['deletions']}")
            print("-" * 80)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 