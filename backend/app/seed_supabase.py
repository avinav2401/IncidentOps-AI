import asyncio
import os

from dotenv import load_dotenv
from supabase import Client, create_client  # type: ignore

load_dotenv()

url: str = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

if not url or not key:
    print("Please set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env")
    exit(1)

supabase: Client = create_client(url, key)

async def main():
    users = [
        {
            "email": "maya.chen@incidentops.dev",
            "password": "demo123",
            "user_metadata": {
                "name": "Maya Chen",
                "role": "incident_commander",
                "avatar_initials": "MC"
            }
        },
        {
            "email": "samir.patel@incidentops.dev",
            "password": "demo123",
            "user_metadata": {
                "name": "Samir Patel",
                "role": "responder",
                "avatar_initials": "SP"
            }
        },
        {
            "email": "lena.ortiz@incidentops.dev",
            "password": "demo123",
            "user_metadata": {
                "name": "Lena Ortiz",
                "role": "admin",
                "avatar_initials": "LO"
            }
        }
    ]

    for user in users:
        print(f"Creating user {user['email']}...")
        try:
            # Note: The admin API is available when using the service_role key
            response = supabase.auth.admin.create_user({
                "email": user["email"],
                "password": user["password"],
                "user_metadata": user["user_metadata"],
                "email_confirm": True
            })
            print(f"Created {user['email']} with ID: {response.user.id}")
        except Exception as e:
            print(f"Failed to create {user['email']}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
