from typing import Dict, Any
import datetime

def generate_incident_report(incident_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a placeholder incident report based on structured incident data.

    In a real scenario, this function would interact with an actual Large Language Model (LLM)
    (e.g., via a local Ollama instance, a free tier API key from OpenAI/Gemini, etc.)
    to produce a detailed, human-readable report.

    The LLM would receive `incident_data` (possibly converted to a prompt) and generate
    sections like Summary, Impact, Mitigation, etc.

    Args:
        incident_data: A dictionary containing details about the incident, such as:
                       - 'id': Incident ID
                       - 'raw_log': Original log entry
                       - 'features': Extracted features
                       - 'anomaly_score_ml': ML anomaly score
                       - 'matched_rules': List of matched rules
                       - 'final_risk_score': Calculated final risk score
                       - 'processed_at': Timestamp of processing

    Returns:
        A dictionary representing the incident report.
    """
    incident_id = incident_data.get("id", "N/A")
    raw_message = incident_data.get("raw_log", {}).get("message", "No message provided.")
    source = incident_data.get("raw_log", {}).get("source", "Unknown source.")
    event_type = incident_data.get("raw_log", {}).get("event_type", "Unknown event type.")
    risk_score = incident_data.get("final_risk_score", 0)
    ml_anomaly = incident_data.get("is_anomaly_ml", False)
    matched_rules = incident_data.get("matched_rules", [])
    processed_at = incident_data.get("processed_at", "N/A")

    # Determine severity level based on final_risk_score
    severity_level = "Low"
    if 31 <= risk_score <= 60:
        severity_level = "Medium"
    elif 61 <= risk_score <= 80:
        severity_level = "High"
    elif 81 <= risk_score <= 100:
        severity_level = "Critical"

    # Mocking LLM-like output
    summary = f"Incident detected with ID {incident_id}. A {severity_level} risk event was identified originating from '{source}' concerning an '{event_type}' event."
    
    explanation_parts = [
        f"The primary event was: '{raw_message}'."
    ]
    if ml_anomaly:
        explanation_parts.append(f"Behavioral anomaly detection flagged this activity as unusual (ML Anomaly Score: {incident_data.get('anomaly_score_ml'):.2f}).")
    if matched_rules:
        rule_names = ", ".join([rule["name"] for rule in matched_rules])
        explanation_parts.append(f"The following security rules were triggered: {rule_names}.")

    possible_attack_type = "Unusual Activity"
    if any("admin" in rule["name"].lower() for rule in matched_rules):
        possible_attack_type = "Privilege Misuse / Unauthorized Access"
    elif any("process" in rule["name"].lower() for rule in matched_rules):
        possible_attack_type = "Execution Attempt"
    elif any("file" in rule["name"].lower() for rule in matched_rules):
        possible_attack_type = "Data Exfiltration / Unauthorized Access"

    mitigation_steps = [
        f"Review log entry ID {incident_id} and raw message for more context.",
        f"Investigate user and system '{source}' involved in the event.",
        f"If a rule was triggered, verify if the activity was legitimate or malicious.",
        f"Consider blocking source IP if activity is confirmed malicious (e.g., {incident_data.get('raw_log', {}).get('metadata', {}).get('ip_address', 'N/A')})."
    ]
    
    # Placeholder for MITRE ATT&CK mapping - a real LLM would infer this
    mitre_attack_mapping = ["T1078 - Valid Accounts", "T1059 - Command and Scripting Interpreter"]

    # Construct the report structure
    report = {
        "Incident ID": str(incident_id),
        "Timestamp": processed_at,
        "Severity Level": severity_level,
        "Final Risk Score": f"{risk_score:.2f}",
        "Summary": summary,
        "Affected Systems/Sources": source,
        "Possible Attack Type": possible_attack_type,
        "Detailed Explanation": " ".join(explanation_parts),
        "Recommended Actions": mitigation_steps,
        "Prevention Strategy": [
            "Implement strong access controls and multi-factor authentication.",
            "Regularly audit administrative activity.",
            "Educate users on security best practices."
        ],
        "MITRE ATT&CK Mapping": mitre_attack_mapping,
        "Executive Summary": f"A {severity_level} risk incident was detected involving {event_type} from {source}. "
                             f"The final risk score was {risk_score:.2f}. Immediate investigation and "
                             f"remediation actions are recommended as detailed in this report to prevent "
                             "potential security breaches."
    }

    return report

# Example Usage (for testing independently)
if __name__ == "__main__":
    sample_incident = {
        "id": 123,
        "raw_log": {
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "server-01",
            "event_type": "authentication",
            "message": "User 'admin' failed multiple logins from external IP 203.0.113.4",
            "metadata": {"user": "admin", "ip_address": "203.0.113.4", "status": "failed", "attempt_count": 5}
        },
        "features": {
            "login_hour": 1, "day_of_week": 5, "is_admin_account": 1, "is_vpn_source": 0,
            "event_type_authentication": 1, "event_type_file_access": 0,
            "event_type_process_exec": 0, "event_type_privilege_escalation": 0,
            "is_weekend":1, "time_of_day_sin":0.05, "time_of_day_cos":0.05,
            "failed_login_count_5min":5, "device_familiarity_score":0, "geo_location_risk_score":0
        },
        "anomaly_score_ml": -0.15,
        "is_anomaly_ml": True,
        "matched_rules": [
            {"name": "Admin Login Outside Business Hours", "severity": "High", "score": 80}
        ],
        "is_anomaly_rule": True,
        "final_risk_score": 85.5,
        "is_anomaly": True,
        "processed_at": datetime.datetime.now().isoformat()
    }
    
    report = generate_incident_report(sample_incident)
    import json
    print(json.dumps(report, indent=2))