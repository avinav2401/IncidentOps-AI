from app.database import SessionLocal
from app.models.incident import Incident
from app.services.intelligence import enrich_incident

db = SessionLocal()
inc = db.query(Incident).first()
if inc:
    res = enrich_incident(db, inc, logs="oom killed timeout", error_rate=95.0)
    print(res)
else:
    print("No incidents")
