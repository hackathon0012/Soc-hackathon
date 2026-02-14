import datetime
from typing import Dict, Any
import math

def extract_features(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts structured features from a raw log entry.

    Args:
        log_entry: A dictionary representing a single log entry.
                   Expected keys: 'timestamp', 'source', 'event_type', 'message', 'metadata'.

    Returns:
        A dictionary of extracted features.
    """
    DEFAULT_FEATURES = {
        "login_hour": 0,
        "day_of_week": 0,
        "is_weekend": 0,
        "time_of_day_sin": 0.0,
        "time_of_day_cos": 0.0,
        "is_admin_account": 0,
        "failed_login_count_5min": 0,
        "device_familiarity_score": 0,
        "is_vpn_source": 0,
        "geo_location_risk_score": 0,
        "event_type_authentication": 0,
        "event_type_file_access": 0,
        "event_type_process_exec": 0,
        "event_type_privilege_escalation": 0,
        # Add any other features here with a default numerical value
    }
    
    features = DEFAULT_FEATURES.copy() # Start with all default features

    # --- Time-based Features ---
    timestamp = log_entry.get("timestamp")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp)
        except ValueError:
            # If parsing fails, use current time as a fallback
            timestamp = datetime.datetime.now() 

    if isinstance(timestamp, datetime.datetime):
        features["login_hour"] = timestamp.hour
        features["day_of_week"] = timestamp.weekday() # Monday is 0, Sunday is 6
        features["is_weekend"] = 1 if timestamp.weekday() >= 5 else 0
        
        # Cyclical features for time of day
        hour_in_day = timestamp.hour + timestamp.minute / 60
        hour_radians = (hour_in_day / 24) * (2 * math.pi)
        features["time_of_day_sin"] = math.sin(hour_radians)
        features["time_of_day_cos"] = math.cos(hour_radians)

    # --- User/Account-based Features ---
    metadata = log_entry.get("metadata", {})
    user = metadata.get("user", "").lower()
    features["is_admin_account"] = 1 if user == "admin" or "root" in user else 0 # Simple heuristic
    # "failed_login_count_5min" and "device_familiarity_score" remain 0 as they are placeholders

    # --- Source/Network-based Features ---
    source = log_entry.get("source", "").lower()
    features["is_vpn_source"] = 1 if "vpn" in source else 0 # Simple heuristic
    # "geo_location_risk_score" remains 0 as it's a placeholder

    # --- Event Type Features ---
    event_type = log_entry.get("event_type", "").lower()
    if "auth" in event_type:
        features["event_type_authentication"] = 1
    if "file" in event_type:
        features["event_type_file_access"] = 1
    if "process" in event_type or "exec" in event_type:
        features["event_type_process_exec"] = 1
    if "privilege" in event_type or "escalation" in event_type:
        features["event_type_privilege_escalation"] = 1

    return features

# Example usage (for testing this module independently)
if __name__ == "__main__":
    sample_log_auth = {
        "timestamp": datetime.datetime.now().isoformat(),
        "source": "linux-server-01",
        "event_type": "authentication",
        "message": "User 'johndoe' logged in successfully from 192.168.1.50",
        "metadata": {"user": "johndoe", "ip_address": "192.168.1.50"}
    }
    sample_log_admin_auth = {
        "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
        "source": "windows-workstation-02",
        "event_type": "authentication",
        "message": "User 'Administrator' failed login from 10.0.0.10",
        "metadata": {"user": "Administrator", "ip_address": "10.0.0.10", "status": "failed"}
    }
    sample_log_file = {
        "timestamp": datetime.datetime.now().isoformat(),
        "source": "cloud-storage-aws",
        "event_type": "file_access",
        "message": "File 'secrets.txt' accessed by 'devuser'",
        "metadata": {"file": "secrets.txt", "user": "devuser", "action": "read"}
    }

    print("Features for sample_log_auth:")
    print(extract_features(sample_log_auth))
    print("\nFeatures for sample_log_admin_auth:")
    print(extract_features(sample_log_admin_auth))
    print("\nFeatures for sample_log_file:")
    print(extract_features(sample_log_file))
