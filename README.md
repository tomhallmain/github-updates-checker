# GitHub Repository Analyzer

A comprehensive tool for analyzing GitHub repositories, their forks, and contributor ecosystems. This project includes both command-line tools and a graphical user interface for exploring repository data.

## Features

### 1. Fork Analyzer (`src/git_updates_checker/analyzers/fork.py`)
Analyzes all forks of a GitHub repository to identify the most active and valuable forks. Calculates an activity score based on:
- Number of stars (up to 50 points)
- Number of commits (up to 25 points)
- Number of pull requests (up to 25 points)
- Recent activity bonus (20 points for commits within the last 30 days)
- File changes compared to the original repository

### 2. Ecosystem Analyzer (`src/git_updates_checker/analyzers/ecosystem.py`)
Analyzes the ecosystem around a repository by examining contributor interests and relationships:
- Finds common repositories that contributors star, fork, or contribute to
- Builds a network graph of contributor relationships
- Identifies shared interests among repository contributors
- Generates visualizations of the contributor network

### 3. GUI Application (`src/git_updates_checker/ui/app.py`)
A PyQt6-based graphical interface that provides:
- Interactive repository analysis
- Table view of analysis results
- Search functionality with field filtering
- Detailed view of file changes and contributor networks
- Support for both fork and ecosystem analysis

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure GitHub token:**
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your GitHub Personal Access Token:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```
   
   To create a GitHub token:
   1. Go to GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
   2. Generate a new token with the `repo` scope (for accessing repository data)

## Usage

Before running, ensure Python can import from the `src` directory:

```bash
# PowerShell
$env:PYTHONPATH="src"

# bash/zsh
export PYTHONPATH=src
```

### Command Line

**Fork Analysis:**
```bash
python -m git_updates_checker.analyzers.fork owner/repository
```

Example:
```bash
python -m git_updates_checker.analyzers.fork octocat/Hello-World
```

**Ecosystem Analysis:**
```bash
python -m git_updates_checker.analyzers.ecosystem owner/repository
```

Example:
```bash
python -m git_updates_checker.analyzers.ecosystem octocat/Hello-World
```

### GUI Application

Launch the graphical interface:
```bash
python -m git_updates_checker.ui.app
```

The GUI allows you to:
- Enter a repository name (format: `owner/repo`)
- Select analysis type (Fork Analysis or Ecosystem Analysis)
- View results in multiple formats (table, search, details)
- Filter and search through results

## Output

### Fork Analyzer Output
- List of all forks sorted by activity score
- Top 10 most active forks with detailed metrics
- File changes summary showing which forks modified which files
- Commit information and change statistics

### Ecosystem Analyzer Output
- Most common starred repositories among contributors
- Most common forked repositories among contributors
- Most common contributed repositories among contributors
- Network graph visualization saved as `interest_graph.png`

## Project Structure

```
git-updates-checker/
├── src/
│   └── git_updates_checker/
│       ├── analyzers/
│       │   ├── fork.py        # Fork analysis module
│       │   └── ecosystem.py   # Ecosystem analysis module
│       └── ui/
│           ├── app.py         # GUI application
│           └── styles.py      # UI stylesheet
├── requirements.txt           # Python dependencies
├── .env.example              # Example environment file
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Important Notes

### Rate Limits
The GitHub API has rate limits. If you're analyzing repositories with many forks or contributors, you might hit these limits. Consider using a GitHub token with higher rate limits if needed.

### API Usage Compliance
This tool uses GitHub's public API endpoints and respects rate limits. It only accesses publicly available repository data and does not perform any actions that modify repositories. The tool complies with GitHub's Terms of Service for API usage.

### Security
- **Never commit your `.env` file** - it contains your personal access token
- The `.gitignore` file is configured to exclude `.env` files and other sensitive data
- All tokens are loaded from environment variables, never hardcoded

## Requirements

- Python 3.7+
- See `requirements.txt` for Python package dependencies
