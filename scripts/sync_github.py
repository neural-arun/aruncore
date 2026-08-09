import os
import sys
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
GITHUB_DIR = BASE_DIR / "data" / "github"

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "neural-arun")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


def fetch_all_repos(username: str):
    print(f"Connecting to GitHub API to fetch public repositories for: {username}...")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN and not GITHUB_TOKEN.startswith("your_"):
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"[ERROR] GitHub API returned status {response.status_code}: {response.text}")
            sys.exit(1)

        repos = response.json()
        print(f"Successfully fetched {len(repos)} repositories from GitHub!")
        return repos
    except Exception as e:
        print(f"[ERROR] Failed to fetch repositories from GitHub: {e}")
        sys.exit(1)


def fetch_repo_readme(username: str, repo_name: str):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN and not GITHUB_TOKEN.startswith("your_"):
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", "")
            encoding = data.get("encoding", "")
            if encoding == "base64" and content:
                return base64.b64decode(content).decode("utf-8", errors="ignore")
            return content
        elif response.status_code == 404:
            return None
        else:
            print(f"  └─ Warning fetching README for {repo_name}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"  └─ Error fetching README for {repo_name}: {e}")
        return None


def save_repo_readme(repo: dict, readme_content: str):
    repo_name = repo.get("name", "unknown_repo")
    html_url = repo.get("html_url", f"https://github.com/{GITHUB_USERNAME}/{repo_name}")
    language = repo.get("language") or "N/A"
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    description = repo.get("description") or "No description provided."
    updated_at = repo.get("updated_at", "N/A")
    topics = repo.get("topics", [])

    repo_dir = GITHUB_DIR / repo_name
    repo_dir.mkdir(parents=True, exist_ok=True)
    target_file = repo_dir / "README.md"

    topics_str = ", ".join(topics) if topics else "None"

    header = f"""---
project_name: {repo_name}
github_url: {html_url}
language: {language}
stars: {stars}
topics: [{topics_str}]
updated_at: {updated_at}
---

# {repo_name}

> **GitHub Repository:** [{html_url}]({html_url})  
> **Primary Language:** {language} | **Stars:** {stars} | **Forks:** {forks}  
> **Description:** {description}

---

"""

    body = readme_content if readme_content else f"*No README.md file found in this repository on GitHub.*\n\n## Overview\n{description}"
    full_content = header + body

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(full_content)

    print(f"  ✓ Saved: data/github/{repo_name}/README.md")


def main():
    print("=" * 60)
    print("ArunCore GitHub Repositories Auto-Sync Pipeline")
    print("=" * 60)

    repos = fetch_all_repos(GITHUB_USERNAME)
    if not repos:
        print("[WARNING] No repositories found.")
        return

    saved_count = 0
    for repo in repos:
        repo_name = repo.get("name")
        if not repo_name or repo.get("fork", False):
            continue

        print(f"Processing repository: {repo_name}...")
        readme_text = fetch_repo_readme(GITHUB_USERNAME, repo_name)
        save_repo_readme(repo, readme_text)
        saved_count += 1

    print("=" * 60)
    print(f"[SUCCESS] GitHub sync complete! Processed {saved_count} repositories into data/github/.")
    print("=" * 60)


if __name__ == "__main__":
    main()
