from app.database import SessionLocal
from app.models.service import Service

try:
    db = SessionLocal()
    srv = db.query(Service).first()
    if srv:
        print("CRITICAL LEVEL IS:", getattr(srv, "critical_level", "MISSING"))
    else:
        print("NO SERVICES FOUND")
except Exception as e:
    print("EXCEPTION:", e)
