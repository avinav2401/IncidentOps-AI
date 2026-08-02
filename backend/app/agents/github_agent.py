"""Real GitHub Commit Agent using httpx."""

import httpx
from sqlalchemy.orm import Session
from app.models.service import Service

async def fetch_recent_commits(service_name: str, workspace_id: str, db: Session) -> list[str]:
    """
    Fetches recent commits for the affected service from GitHub API.
    """
    service_record = db.query(Service).filter(
        Service.workspace_id == workspace_id,
        Service.name == service_name
    ).first()
    
    if not service_record or not service_record.repository:
        return [f"No GitHub repository linked to service '{service_name}'."]
        
    repo = service_record.repository.strip()
    
    if "github.com/" in repo:
        repo = repo.split("github.com/")[-1]
        
    if repo.endswith(".git"):
        repo = repo[:-4]
    repo = repo.strip("/")
        
    api_url = f"https://api.github.com/repos/{repo}/commits"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url, 
                headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "IncidentOps-AI"},
                params={"per_page": 5}
            )
            
            if response.status_code != 200:
                return [f"Failed to fetch commits from {repo} (Status {response.status_code})."]
                
            commits_data = response.json()
            
            formatted_commits = []
            for item in commits_data:
                sha = item.get("sha", "")[:7]
                msg = item.get("commit", {}).get("message", "").split("\n")[0]
                author = item.get("commit", {}).get("author", {}).get("name", "Unknown")
                date = item.get("commit", {}).get("author", {}).get("date", "")
                formatted_commits.append(f"Commit {sha} by {author}: {msg} ({date})")
                
            if not formatted_commits:
                return [f"No recent commits found in {repo}."]
                
            return formatted_commits
            
    except Exception as e:
        return [f"Error fetching commits from {repo}: {str(e)}"]
