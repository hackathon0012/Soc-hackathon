from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON
from database import Base
from sqlalchemy.sql import func
import datetime

class ProcessedLog(Base):
    __tablename__ = "processed_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Raw Log Data
    raw_timestamp = Column(DateTime, default=datetime.datetime.now)
    raw_source = Column(String, index=True)
    raw_event_type = Column(String, index=True)
    raw_message = Column(String)
    raw_metadata = Column(JSON) # Store metadata as JSON

    # Extracted Features (for ML and Rules)
    features = Column(JSON) # Store all extracted features as JSON

    # Anomaly Detection Results
    anomaly_score_ml = Column(Float, default=0.0)
    is_anomaly_ml = Column(Boolean, default=False)
    
    # Rule Matching Results
    matched_rules = Column(JSON) # Store list of matched rules as JSON
    is_anomaly_rule = Column(Boolean, default=False)

    # Final Risk Score
    final_risk_score = Column(Float, default=0.0, index=True)
    is_anomaly = Column(Boolean, default=False, index=True) # Overall anomaly status

    # Processing Timestamp
    processed_at = Column(DateTime, default=func.now())
