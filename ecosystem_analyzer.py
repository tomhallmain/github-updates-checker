import os
import sys
from typing import List, Dict, Any, Set, Counter
from github import Github
from github.Repository import Repository
from github.NamedUser import NamedUser
from collections import defaultdict, Counter
from dotenv import load_dotenv
from tqdm import tqdm
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class EcosystemAnalyzer:
    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.user_cache = {}  # Cache for user data to avoid rate limits
        
    def get_repository(self, repo_name: str) -> Repository:
        """Get the repository object from GitHub."""
        return self.github.get_repo(repo_name)
    
    def get_user_data(self, username: str) -> Dict[str, Any]:
        """Get user data with caching to avoid rate limits."""
        if username in self.user_cache:
            return self.user_cache[username]
            
        try:
            user = self.github.get_user(username)
            data = {
                'name': user.name,
                'login': user.login,
                'starred_repos': set(),
                'forked_repos': set(),
                'contributed_repos': set()
            }
            
            # Get starred repositories
            print(f"Fetching starred repos for {username}...")
            for repo in user.get_starred():
                data['starred_repos'].add(repo.full_name)
            
            # Get forked repositories
            print(f"Fetching forked repos for {username}...")
            for repo in user.get_repos():
                if repo.fork:
                    data['forked_repos'].add(repo.full_name)
            
            # Get contributed repositories (repos with commits)
            print(f"Fetching contributed repos for {username}...")
            for repo in user.get_repos():
                try:
                    commits = repo.get_commits(author=username)
                    if commits.totalCount > 0:
                        data['contributed_repos'].add(repo.full_name)
                except Exception:
                    continue
            
            self.user_cache[username] = data
            return data
            
        except Exception as e:
            print(f"Error fetching data for user {username}: {str(e)}")
            return None
    
    def get_repository_contributors(self, repo: Repository) -> List[str]:
        """Get all contributors to a repository."""
        contributors = set()
        
        # Get direct contributors
        for contributor in repo.get_contributors():
            contributors.add(contributor.login)
        
        # Get fork owners
        for fork in repo.get_forks():
            contributors.add(fork.owner.login)
        
        return list(contributors)
    
    def find_common_interests(self, contributors: List[str]) -> Dict[str, Any]:
        """Find common interests among contributors."""
        common_data = {
            'starred_repos': Counter(),
            'forked_repos': Counter(),
            'contributed_repos': Counter()
        }
        
        # Collect data from all contributors
        for username in tqdm(contributors, desc="Analyzing contributors"):
            user_data = self.get_user_data(username)
            if user_data:
                common_data['starred_repos'].update(user_data['starred_repos'])
                common_data['forked_repos'].update(user_data['forked_repos'])
                common_data['contributed_repos'].update(user_data['contributed_repos'])
        
        return common_data
    
    def build_interest_graph(self, contributors: List[str]) -> nx.Graph:
        """Build a graph of contributor interests."""
        G = nx.Graph()
        
        # Add contributors as nodes
        for username in contributors:
            G.add_node(username, type='contributor')
        
        # Add common interests as edges
        for i, user1 in enumerate(contributors):
            data1 = self.get_user_data(user1)
            if not data1:
                continue
                
            for user2 in contributors[i+1:]:
                data2 = self.get_user_data(user2)
                if not data2:
                    continue
                
                # Calculate similarity based on common interests
                common_stars = len(data1['starred_repos'] & data2['starred_repos'])
                common_forks = len(data1['forked_repos'] & data2['forked_repos'])
                common_contributions = len(data1['contributed_repos'] & data2['contributed_repos'])
                
                similarity = common_stars + common_forks + common_contributions
                if similarity > 0:
                    G.add_edge(user1, user2, weight=similarity)
        
        return G
    
    def analyze_ecosystem(self, repo_name: str) -> Dict[str, Any]:
        """Analyze the ecosystem around a repository."""
        print(f"Analyzing ecosystem for repository: {repo_name}")
        
        # Get the repository
        repo = self.get_repository(repo_name)
        
        # Get all contributors
        contributors = self.get_repository_contributors(repo)
        print(f"Found {len(contributors)} contributors")
        
        # Find common interests
        common_interests = self.find_common_interests(contributors)
        
        # Build interest graph
        interest_graph = self.build_interest_graph(contributors)
        
        return {
            'common_interests': common_interests,
            'interest_graph': interest_graph,
            'contributors': contributors
        }
    
    def visualize_interest_graph(self, G: nx.Graph, output_file: str = 'interest_graph.png'):
        """Visualize the interest graph."""
        plt.figure(figsize=(12, 8))
        
        # Use spring layout for better visualization
        pos = nx.spring_layout(G)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                             node_size=500, alpha=0.6)
        
        # Draw edges with varying thickness based on weight
        edges = G.edges(data=True)
        weights = [data['weight'] for _, _, data in edges]
        nx.draw_networkx_edges(G, pos, width=weights, alpha=0.4)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        plt.title("Contributor Interest Network")
        plt.axis('off')
        plt.savefig(output_file)
        plt.close()

def main():
    # Load GitHub token from environment variable
    load_dotenv()
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token in a .env file or environment variable")
        sys.exit(1)
    
    if len(sys.argv) != 2:
        print("Usage: python ecosystem_analyzer.py <repository_name>")
        print("Example: python ecosystem_analyzer.py octocat/Hello-World")
        sys.exit(1)
    
    repo_name = sys.argv[1]
    analyzer = EcosystemAnalyzer(github_token)
    
    try:
        results = analyzer.analyze_ecosystem(repo_name)
        
        # Print common interests
        print("\nCommon Interests Analysis:")
        print("-" * 80)
        
        # Print most common starred repositories
        print("\nMost Common Starred Repositories:")
        for repo, count in results['common_interests']['starred_repos'].most_common(10):
            print(f"{repo}: {count} contributors")
        
        # Print most common forked repositories
        print("\nMost Common Forked Repositories:")
        for repo, count in results['common_interests']['forked_repos'].most_common(10):
            print(f"{repo}: {count} contributors")
        
        # Print most common contributed repositories
        print("\nMost Common Contributed Repositories:")
        for repo, count in results['common_interests']['contributed_repos'].most_common(10):
            print(f"{repo}: {count} contributors")
        
        # Generate and save the interest graph visualization
        print("\nGenerating interest graph visualization...")
        analyzer.visualize_interest_graph(results['interest_graph'])
        print("Graph saved as 'interest_graph.png'")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 