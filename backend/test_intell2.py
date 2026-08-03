from app.database import SessionLocal
from app.models.incident import Incident

db = SessionLocal()
inc = db.query(Incident).first()
if inc:
    print(inc.severity)
