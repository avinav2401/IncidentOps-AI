import re
import os

path = r"C:\Users\avina\OneDrive\Desktop\ai\backend\app\services\incident_service.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add _get_incident helper and import func
content = content.replace("from sqlalchemy.orm import Session\n", "from sqlalchemy.orm import Session\nfrom sqlalchemy import func\n")

helper = """
def _get_incident(db: Session, workspace_id: str, incident_id: str):
    return (
        db.query(Incident)
        .filter(Incident.workspace_id == workspace_id, (Incident.id == incident_id) | (Incident.incident_number == incident_id))
        .first()
    )
"""

content = content.replace("# ── List / Read ────────────────────────────────────────────────────────", helper + "\n\n# ── List / Read ────────────────────────────────────────────────────────")

# 2. Replace the duplicated lookup
lookup_pattern = r"""\s*incident\s*=\s*\(\s*db\.query\(Incident\)\s*\.filter\(Incident\.workspace_id == workspace_id,\s*\(Incident\.id == incident_id\) \| \(Incident\.incident_number == incident_id\)\)\s*\.first\(\)\s*\)"""
content = re.sub(lookup_pattern, "\n    incident = _get_incident(db, workspace_id, incident_id)", content)

lookup_pattern2 = r"""\s*row\s*=\s*\(\s*db\.query\(Incident\)\s*\.filter\(Incident\.workspace_id == workspace_id,\s*\(Incident\.id == incident_id\) \| \(Incident\.incident_number == incident_id\)\)\s*\.first\(\)\s*\)"""
content = re.sub(lookup_pattern2, "\n    row = _get_incident(db, workspace_id, incident_id)", content)

# 3. Fix delete_incident
delete_old = """    if not incident:
        return False
    _add_audit(db, "incident", incident.id, "incident.deleted", actor, f"Deleted {incident.incident_number}.")
    db.delete(incident)
    db.commit()"""

delete_new = """    if not incident:
        return False
    
    # Capture values before delete
    inc_id = incident.id
    inc_num = incident.incident_number
    
    db.delete(incident)
    # Write audit log after delete
    _add_audit(db, "incident", inc_id, "incident.deleted", actor, f"Deleted {inc_num}.")
    db.commit()"""
content = content.replace(delete_old, delete_new)

# 4. Fix create_incident
create_old = """    now = _utcnow()
    count = db.query(Incident).filter(Incident.workspace_id == workspace_id).count()
    incident = Incident(
        id=f"inc_{_uid()}",
        workspace_id=workspace_id,
        incident_number=f"INC-{now.year}-{count + 38:03d}","""

create_new = """    now = _utcnow()
    
    max_inc = db.query(func.max(Incident.incident_number)).filter(
        Incident.workspace_id == workspace_id,
        Incident.incident_number.like(f"INC-{now.year}-%")
    ).scalar()
    
    if max_inc:
        try:
            next_num = int(max_inc.split("-")[-1]) + 1
        except ValueError:
            next_num = 1
    else:
        next_num = 1
        
    incident = Incident(
        id=f"inc_{_uid()}",
        workspace_id=workspace_id,
        incident_number=f"INC-{now.year}-{next_num:03d}","""
content = content.replace(create_old, create_new)

# 5. Fix audit_logs
audit_old = """        # If no incident_id is provided, we should only return audit logs for incidents in this workspace.
        # As a simplified approach for now, we just join.
        incident_ids = [row[0] for row in db.query(Incident.id).filter(Incident.workspace_id == workspace_id).all()]
        q = q.filter(AuditLog.entity_id.in_(incident_ids))"""

audit_new = """        # If no incident_id is provided, we should only return audit logs for incidents in this workspace.
        incident_ids = [row[0] for row in db.query(Incident.id).filter(Incident.workspace_id == workspace_id).all()]
        
        from sqlalchemy import or_
        filters = [AuditLog.entity_id.in_(incident_ids)]
        for i_id in incident_ids:
            filters.append(AuditLog.metadata_raw.contains(i_id))
        
        if filters:
            q = q.filter(or_(*filters))
        else:
            return []"""
content = content.replace(audit_old, audit_new)

# 6. Remove actor default values
content = content.replace('actor: str = "Maya Chen"', 'actor: str')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done refactoring incident_service.py")
