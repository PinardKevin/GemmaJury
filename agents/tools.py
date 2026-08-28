"""Tools the panel uses to inspect a public submission."""

from __future__ import annotations

import json
import re
from urllib.parse import urlparse

import httpx

GITHUB_RE = re.compile(
    r"https?://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)"
)

MAX_FILE_CHARS = 12_000


def _client() -> httpx.Client:
    return httpx.Client(timeout=20.0, follow_redirects=True, headers={"User-Agent": "GemmaJury/1.0"})


def _parse_github(url: str) -> tuple[str, str] | None:
    match = GITHUB_RE.search(url or "")
    if not match:
        return None
    repo = match.group("repo").removesuffix(".git")
    return match.group("owner"), repo


def fetch_github_evidence(repo_url: str) -> str:
    """Fetch README, default branch, languages, and a shallow file tree from a public GitHub repo."""
    parsed = _parse_github(repo_url)
    if not parsed:
        return json.dumps({"error": "not_a_github_url", "url": repo_url})
    owner, repo = parsed
    api = f"https://api.github.com/repos/{owner}/{repo}"
    with _client() as client:
        repo_res = client.get(api)
        if repo_res.status_code == 404:
            return json.dumps({"error": "repo_not_found", "url": repo_url})
        repo_res.raise_for_status()
        meta = repo_res.json()
        branch = meta.get("default_branch") or "main"
        readme_res = client.get(f"{api}/readme", headers={"Accept": "application/vnd.github.raw"})
        readme = readme_res.text[:8000] if readme_res.status_code == 200 else ""
        lang_res = client.get(f"{api}/languages")
        languages = lang_res.json() if lang_res.status_code == 200 else {}
        tree_res = client.get(f"{api}/git/trees/{branch}?recursive=1")
        files: list[str] = []
        if tree_res.status_code == 200:
            for item in tree_res.json().get("tree", []):
                if item.get("type") == "blob":
                    files.append(item.get("path", ""))
                    if len(files) >= 80:
                        break
    return json.dumps(
        {
            "owner": owner,
            "repo": repo,
            "full_name": meta.get("full_name"),
            "description": meta.get("description"),
            "stars": meta.get("stargazers_count"),
            "default_branch": branch,
            "license": (meta.get("license") or {}).get("spdx_id"),
            "languages": languages,
            "readme": readme,
            "files": files,
            "html_url": meta.get("html_url"),
        },
        ensure_ascii=False,
    )


def fetch_github_file(repo_url: str, path: str) -> str:
    """Fetch one text file from a public GitHub repository."""
    parsed = _parse_github(repo_url)
    if not parsed:
        return json.dumps({"error": "not_a_github_url", "url": repo_url})
    owner, repo = parsed
    api = f"https://api.github.com/repos/{owner}/{repo}/contents/{path.lstrip('/')}"
    with _client() as client:
        res = client.get(api, headers={"Accept": "application/vnd.github.raw"})
        if res.status_code != 200:
            return json.dumps({"error": "file_not_found", "path": path, "status": res.status_code})
        text = res.text[:MAX_FILE_CHARS]
    return json.dumps({"path": path, "content": text}, ensure_ascii=False)


def fetch_demo_evidence(demo_url: str) -> str:
    """Fetch the public demo page title, status, and a text excerpt."""
    url = (demo_url or "").strip()
    if not url.startswith("http"):
        return json.dumps({"error": "not_a_url", "url": demo_url})
    parsed = urlparse(url)
    with _client() as client:
        try:
            res = client.get(url)
        except httpx.HTTPError as exc:
            return json.dumps({"error": "fetch_failed", "url": url, "detail": str(exc)})
    title_match = re.search(r"<title[^>]*>(.*?)</title>", res.text, re.I | re.S)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
    text = re.sub(r"<script[\s\S]*?</script>", " ", res.text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()[:4000]
    return json.dumps(
        {
            "url": url,
            "host": parsed.netloc,
            "status": res.status_code,
            "content_type": res.headers.get("content-type"),
            "title": title,
            "excerpt": text,
        },
        ensure_ascii=False,
    )
