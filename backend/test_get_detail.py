from app.database import SessionLocal
from app.services import incident_service as svc

db = SessionLocal()
inc = svc.get_detail(db, "INC-2026-041")
print(f"inc[id] = {inc['id']}")
print(f"inc[incident_number] = {inc['incident_number']}")
