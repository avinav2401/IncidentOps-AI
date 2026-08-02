import sys
sys.path.append('.')
from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import create_access_token, decode_access_token

db = SessionLocal()
user = db.query(User).order_by(User.created_at.desc()).first()
print(f"User ID: {user.id}")

token = create_access_token({"sub": str(user.id)})
print(f"Token: {token}")

payload = decode_access_token(token)
print(f"Payload: {payload}")
