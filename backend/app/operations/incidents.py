import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.data.database.models import IncidentDB

logger = logging.getLogger(__name__)

class IncidentManager:
    """
    Manages operational incidents for observability and reliability.
    """
    def __init__(self):
        pass

    def log_incident(
        self,
        db: Session,
        severity: str,
        category: str,
        message: str,
        instrument: str = None,
        provider: str = None
    ) -> IncidentDB:
        """
        Logs a new incident persistently into the database.
        Severity options: INFO, WARNING, ERROR, CRITICAL
        """
        if severity not in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
            severity = "INFO"
            
        incident = IncidentDB(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            category=category,
            instrument=instrument,
            provider=provider,
            message=message
        )
        
        try:
            db.add(incident)
            db.commit()
            db.refresh(incident)
            
            log_msg = f"INCIDENT [{severity}] {category} | {instrument or 'SYS'} | {message}"
            if severity in ["ERROR", "CRITICAL"]:
                logger.error(log_msg)
            elif severity == "WARNING":
                logger.warning(log_msg)
            else:
                logger.info(log_msg)
                
            return incident
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to persist incident: {e}")
            return None

    def resolve_incident(self, db: Session, incident_id: str) -> bool:
        incident = db.query(IncidentDB).filter_by(id=incident_id).first()
        if incident:
            incident.resolved = True
            incident.resolved_at = datetime.now(timezone.utc)
            db.commit()
            return True
        return False
        
    def get_active_incidents(self, db: Session, limit: int = 50):
        return db.query(IncidentDB).filter_by(resolved=False).order_by(IncidentDB.timestamp.desc()).limit(limit).all()
        
incident_manager = IncidentManager()
