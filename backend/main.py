from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import json # Import json for handling JSON fields properly

from feature_engineering import extract_features
from anomaly_detection import AnomalyDetector
from rules import apply_rules, SEVERITY_SCORES
from llm_reporter import generate_incident_report

from fastapi.middleware.cors import CORSMiddleware

# Database imports
from database import SessionLocal, engine, Base
from models import ProcessedLog # Import our SQLAlchemy model

app = FastAPI(title="AI-SOC Lite Backend")

# NEW: CORS Middleware configuration
origins = [
    "http://localhost",
    "http://localhost:5173",  # React frontend's default port
    "http://127.0.0.1:5173",  # React frontend's default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Anomaly Detector (model will be trained/loaded via DB)
anomaly_detector = AnomalyDetector(contamination=0.01)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Startup event to create database tables
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine) # Create all tables if they don't exist
    # Load model if available (for persistence across restarts)
    # For now, we'll keep training as an explicit endpoint.
    # In a real app, model persistence would be handled here.

# Define a model for the incoming log (same as before)
class LogEntry(BaseModel):
    timestamp: datetime.datetime = datetime.datetime.now()
    source: str
    event_type: str
    message: str
    metadata: Dict[str, Any] = {}

# --- Helper to calculate risk score ---
def calculate_risk_score(anomaly_score: float, matched_rules: List[Dict[str, Any]]) -> float:
    # Scale anomaly_score from Isolation Forest's range to 0-100
    # Isolation Forest decision_function typically ranges from -0.5 to 0.5 (or similar)
    # A simple linear scaling, where lower score is higher risk
    # Clamp anomaly_score to a reasonable range for scaling to prevent extreme values from distorting
    # Based on sklearn docs, scores are between -1 and 1. We'll use a pragmatic range.
    clamped_anomaly_score = max(-0.6, min(0.6, anomaly_score)) # Adjust these bounds based on observed scores

    # Normalize to 0-1 range (0=most normal, 1=most anomalous)
    normalized_anomaly_risk = (0.6 - clamped_anomaly_score) / 1.2 # (Max_score - current) / (Max_score - Min_score)

    scaled_anomaly_score = normalized_anomaly_risk * 100

    # Determine max rule severity score
    max_rule_score = 0
    if matched_rules:
        max_rule_score = max(rule["score"] for rule in matched_rules)

    # Placeholder for Geo Risk Modifier (0 for now)
    geo_risk_modifier = 0

    # Final Risk Score = (Anomaly Score × 0.6) + (Rule Severity × 0.4) + (Geo Risk Modifier)
    final_risk_score = (scaled_anomaly_score * 0.6) + (max_rule_score * 0.4) + geo_risk_modifier

    # Ensure score is within 0-100 range
    return max(0.0, min(100.0, final_risk_score))

# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "AI-SOC Lite Backend is running!"}

@app.post("/ingest-log")
async def ingest_log(log_entry: LogEntry, db: Session = Depends(get_db)):
    """
    Endpoint to ingest security logs, extract features, predict anomaly scores,
    apply rules, and calculate a final risk score.
    """
    # 1. Extract features
    raw_log_dict = log_entry.dict()
    features = extract_features(raw_log_dict)

    # 2. Predict anomaly score if model is trained
    anomaly_score = 0.0
    is_anomaly_ml = False # Flag from ML model
    if anomaly_detector.model:
        print(f"Features before prediction: {features}") # Debugging line
        anomaly_score = anomaly_detector.predict(features)
        # Isolation Forest's decision_function: negative values are usually anomalies
        # The 'offset_' attribute is the threshold learned by the model
        if anomaly_score < anomaly_detector.model.offset_:
             is_anomaly_ml = True
    else:
        print("Anomaly detector not yet trained. Ingesting log without anomaly scoring.")

    # 3. Apply rules
    matched_rules = apply_rules(features)
    is_anomaly_rule = bool(matched_rules) # Flag if any rule matched

    # 4. Calculate final risk score
    final_risk_score = calculate_risk_score(anomaly_score, matched_rules)

    # Determine overall anomaly status (if either ML or Rule flags it)
    is_anomaly = is_anomaly_ml or is_anomaly_rule
    
    # 5. Create new ProcessedLog entry and add to DB
    db_log = ProcessedLog(
        raw_timestamp=log_entry.timestamp,
        raw_source=log_entry.source,
        raw_event_type=log_entry.event_type,
        raw_message=log_entry.message,
        raw_metadata=log_entry.metadata,
        features=features,
        anomaly_score_ml=anomaly_score,
        is_anomaly_ml=is_anomaly_ml,
        matched_rules=matched_rules,
        is_anomaly_rule=is_anomaly_rule,
        final_risk_score=final_risk_score,
        is_anomaly=is_anomaly,
        processed_at=datetime.datetime.now()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log) # Refresh to get the auto-generated ID

    print(f"Log ID: {db_log.id} | Message: {raw_log_dict['message']} | ML Anomaly: {is_anomaly_ml} (Score: {anomaly_score:.2f}) | Rules Matched: {len(matched_rules)} | Final Risk: {final_risk_score:.2f} | Overall Anomaly: {is_anomaly}")
    return {
        "status": "success",
        "message": "Log ingested and processed",
        "log_id": db_log.id, # Return ID from DB
        "anomaly_score_ml": anomaly_score,
        "is_anomaly_ml": is_anomaly_ml,
        "matched_rules": matched_rules,
        "is_anomaly_rule": is_anomaly_rule,
        "final_risk_score": final_risk_score,
        "is_anomaly": is_anomaly
    }

@app.get("/logs")
async def get_logs(db: Session = Depends(get_db)):
    """
    Retrieve all ingested logs with their extracted features, anomaly scores, and risk scores.
    """
    logs = db.query(ProcessedLog).order_by(ProcessedLog.processed_at.desc()).all()
    # Convert SQLAlchemy objects to dict for JSON serialization
    return {"logs": [log.__dict__ for log in logs]}

@app.post("/train-model")
async def train_model(db: Session = Depends(get_db)):
    """
    Endpoint to train the Isolation Forest anomaly detection model
    using currently ingested 'normal' logs.
    """
    all_logs = db.query(ProcessedLog).all()
    if not all_logs:
        raise HTTPException(status_code=400, detail="No logs ingested yet to train the model.")

    # Extract features from all logs
    all_features = [log.features for log in all_logs]

    try:
        anomaly_detector.train(all_features)
        return {"status": "success", "message": f"Anomaly detection model trained on {len(all_features)} samples."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@app.get("/anomalies")
async def get_anomalies(db: Session = Depends(get_db)):
    """
    Retrieve all logs identified as anomalies (either by ML or rules), sorted by risk score.
    """
    anomalies = db.query(ProcessedLog).filter(ProcessedLog.is_anomaly == True).order_by(ProcessedLog.final_risk_score.desc()).all()
    return {"anomalies": [log.__dict__ for log in anomalies], "count": len(anomalies)}

@app.get("/risk-dashboard-summary")
async def get_risk_dashboard_summary(db: Session = Depends(get_db)):
    """
    Provides a summary of current risk levels for dashboard display.
    """
    total_logs = db.query(ProcessedLog).count()
    if total_logs == 0:
        return {"total_logs": 0, "total_anomalies": 0, "average_risk_score": 0.0, "risk_distribution": {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}}

    total_anomalies = db.query(ProcessedLog).filter(ProcessedLog.is_anomaly == True).count()
    
    # Calculate average risk score
    # Use func.avg for database-level aggregation
    average_risk_score_result = db.query(func.avg(ProcessedLog.final_risk_score)).scalar()
    average_risk_score = float(average_risk_score_result) if average_risk_score_result is not None else 0.0

    # Categorize risk distribution
    low_risk = db.query(ProcessedLog).filter(ProcessedLog.final_risk_score >= 0, ProcessedLog.final_risk_score <= 30).count()
    medium_risk = db.query(ProcessedLog).filter(ProcessedLog.final_risk_score > 30, ProcessedLog.final_risk_score <= 60).count()
    high_risk = db.query(ProcessedLog).filter(ProcessedLog.final_risk_score > 60, ProcessedLog.final_risk_score <= 80).count()
    critical_risk = db.query(ProcessedLog).filter(ProcessedLog.final_risk_score > 80, ProcessedLog.final_risk_score <= 100).count()

    risk_distribution = {
        "Low": low_risk,
        "Medium": medium_risk,
        "High": high_risk,
        "Critical": critical_risk
    }

    return {
        "total_logs": total_logs,
        "total_anomalies": total_anomalies,
        "average_risk_score": f"{average_risk_score:.2f}",
        "risk_distribution": risk_distribution
    }

@app.get("/generate-incident-report/{log_id}")
async def get_incident_report(log_id: int, db: Session = Depends(get_db)):
    """
    Generates an incident report for a specific anomalous log entry using the LLM reporter.
    """
    incident_data = db.query(ProcessedLog).filter(ProcessedLog.id == log_id).first()
    
    if not incident_data:
        raise HTTPException(status_code=404, detail="Log entry not found.")

    if not incident_data.is_anomaly:
        raise HTTPException(status_code=400, detail=f"Log entry ID {log_id} is not marked as an anomaly. Reports can only be generated for anomalies.")

    try:
        # Convert SQLAlchemy model object to a dictionary for the reporter
        report = generate_incident_report(incident_data.__dict__)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

