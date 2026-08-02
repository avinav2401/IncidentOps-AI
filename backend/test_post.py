import urllib.request
import json
import sys
sys.path.append('.')
from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import create_access_token

db = SessionLocal()
user = db.query(User).order_by(User.created_at.desc()).first()
token = create_access_token({"sub": str(user.id)})

url = 'http://127.0.0.1:8000/api/v1/workspaces'
data = json.dumps({"name": "Test", "industry": "Tech", "company_size": "1-10"}).encode('utf-8')
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

req = urllib.request.Request(url, data=data, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as response:
        print(response.status)
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.read().decode('utf-8'))
