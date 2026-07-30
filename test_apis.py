import os
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

async def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Not configured"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            if resp.status_code == 200:
                return "[OK] (Authenticated successfully)"
            else:
                return f"[FAIL]: HTTP {resp.status_code} - {resp.text[:100]}"
    except Exception as e:
        return f"[FAIL]: {str(e)}"

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Not configured"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0
            )
            if resp.status_code == 200:
                return "[OK] (Authenticated successfully)"
            else:
                return f"[FAIL]: HTTP {resp.status_code} - {resp.text[:100]}"
    except Exception as e:
        return f"[FAIL]: {str(e)}"

async def test_slack():
    token = os.getenv("SLACK_BOT_TOKEN")
    channel = os.getenv("SLACK_CHANNEL")
    
    if not token:
        return "Not configured (SLACK_BOT_TOKEN missing)"
    if not channel:
        return "[FAIL] (SLACK_BOT_TOKEN is set, but SLACK_CHANNEL is missing)"
        
    try:
        async with httpx.AsyncClient() as client:
            # We use conversations.info to check if the bot can see the channel without actually posting a message
            resp = await client.post(
                "https://slack.com/api/conversations.info",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={"channel": channel},
                timeout=10.0
            )
            data = resp.json()
            if data.get("ok"):
                channel_name = data.get("channel", {}).get("name", "unknown")
                return f"[OK] (Bot has access to channel #{channel_name})"
            else:
                return f"[FAIL]: {data.get('error')} - Ensure the bot is invited to the channel!"
    except Exception as e:
        return f"[FAIL]: {str(e)}"

async def test_jira():
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")
    base_url = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    project = os.getenv("JIRA_PROJECT_KEY")
    
    if not all([email, token, base_url, project]):
        return "Not fully configured (Missing one of EMAIL, TOKEN, BASE_URL, or PROJECT_KEY)"
        
    try:
        import base64
        auth_string = f"{email}:{token}"
        auth_encoded = base64.b64encode(auth_string.encode()).decode()
        
        async with httpx.AsyncClient() as client:
            # Check if project exists and we have access
            resp = await client.get(
                f"{base_url}/rest/api/3/project/{project}",
                headers={
                    "Authorization": f"Basic {auth_encoded}",
                    "Accept": "application/json"
                },
                timeout=10.0
            )
            if resp.status_code == 200:
                proj_name = resp.json().get("name", "unknown")
                return f"[OK] (Access verified for project '{proj_name}')"
            else:
                # Try to list all projects to help them
                projects_resp = await client.get(
                    f"{base_url}/rest/api/3/project",
                    headers={"Authorization": f"Basic {auth_encoded}", "Accept": "application/json"},
                    timeout=10.0
                )
                if projects_resp.status_code == 200:
                    available_keys = [p.get("key") for p in projects_resp.json()]
                    return f"[FAIL]: Project '{project}' not found! But your API key works. Available project keys are: {available_keys}"
                return f"[FAIL]: HTTP {resp.status_code} - Check URL, Email, or Token."
    except Exception as e:
        return f"[FAIL]: {str(e)}"

async def main():
    print("--- API Connectivity Test ---")
    
    print("\n1. OpenAI:", await test_openai())
    print("\n2. Groq:", await test_groq())

    print("\n4. Slack:", await test_slack())
    print("\n5. Jira:", await test_jira())
    
    print("\n-----------------------------")

if __name__ == "__main__":
    asyncio.run(main())
