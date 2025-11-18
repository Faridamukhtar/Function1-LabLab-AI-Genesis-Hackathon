import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

# -----------------------------
# GitHub API Authentication
# -----------------------------
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "AI-Hiring-Pipeline",
}

# Add token if present (recommended)
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


# -----------------------------
# Parse GitHub URL
# -----------------------------
def parse_github_repo_url(url: str):
    """
    Takes a GitHub URL like:
    https://github.com/user/repo
    OR https://github.com/user/repo/tree/branch/path

    Returns:
      owner, repo, branch, path
    """
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repo URL")

    owner = parts[0]
    repo = parts[1]

    # Default branch
    branch = "main"
    path = ""

    # Optional: /tree/<branch>/folder...
    if len(parts) >= 4 and parts[2] == "tree":
        branch = parts[3]
        path = "/".join(parts[4:])

    return owner, repo, branch, path


# -----------------------------
# Fetch repository contents
# -----------------------------
def fetch_repo_file_tree(owner: str, repo: str, branch: str, path: str = ""):
    """
    Fetches a folder or repo root from GitHub.

    Uses GitHub API, not raw URLs. Supports:
    - free-tier
    - non-owner access
    """

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    resp = requests.get(api_url, headers=HEADERS)

    if resp.status_code == 403:
        raise RuntimeError(
            "GitHub 403 Forbidden\n"
            "Cause: Missing/invalid token OR rate-limited.\n"
            "Fix: Add GITHUB_TOKEN to .env"
        )

    if resp.status_code == 404:
        raise RuntimeError("GitHub returned 404: Repo or path not found")

    if resp.status_code >= 400:
        raise RuntimeError(f"GitHub error {resp.status_code}: {resp.text}")

    return resp.json()


# -----------------------------
# Download raw file
# -----------------------------
def download_raw_file(raw_url: str) -> str:
    """
    Downloads raw GitHub file content.
    """
    resp = requests.get(raw_url, headers=HEADERS)

    if resp.status_code == 403:
        raise RuntimeError("GitHub raw file fetch blocked: Add GITHUB_TOKEN")

    if resp.status_code != 200:
        raise RuntimeError(f"Failed to download file {raw_url}: {resp.status_code}")

    return resp.text


# -----------------------------
# Recursively fetch all files
# -----------------------------
def fetch_github_repo(url: str) -> dict:
    """
    Fetch an ENTIRE repo (all files) into a dict:
    {
        "file1.py": "content...",
        "folder/file2.js": "content..."
    }
    """
    print(f"📥 Fetching GitHub repository: {url}")

    owner, repo, branch, path = parse_github_repo_url(url)
    tree = fetch_repo_file_tree(owner, repo, branch, path)

    collected = {}

    def walk(node_list, prefix=""):
        for node in node_list:
            node_type = node.get("type")
            node_path = node.get("path")
            node_name = node.get("name")

            if node_type == "file":
                raw_url = node["download_url"]
                print(f"   📄 Downloading: {node_path}")
                collected[node_path] = download_raw_file(raw_url)

            elif node_type == "dir":
                print(f"   📁 Entering folder: {node_path}")
                sub = fetch_repo_file_tree(owner, repo, branch, node_path)
                walk(sub, prefix=node_path + "/")

    # Repo root may return single dict OR list
    if isinstance(tree, dict):
        tree = [tree]

    walk(tree)
    print(f"   ✅ Fetched {len(collected)} files successfully")

    return collected


# -----------------------------
# MAIN API for your pipeline
# -----------------------------
def fetch_github_code(repo_url: str) -> dict:
    """
    Wrapper for pipeline usage:
    - Validates URL
    - Fetches entire repo
    - Returns dict of files
    """
    try:
        return fetch_github_repo(repo_url)
    except Exception as e:
        print(f"❌ GitHub fetch error: {e}")
        raise RuntimeError(f"Failed to fetch code from GitHub: {e}")
