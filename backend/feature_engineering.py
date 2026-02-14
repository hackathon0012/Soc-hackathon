import datetime
from typing import Dict, Any

def extract_features(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts structured features from a raw log entry.

    Args:
        log_entry: A dictionary representing a single log entry.
                   Expected keys: 'timestamp', 'source', 'event_type', 'message', 'metadata'.

    Returns:
        A dictionary of extracted features.
    """
    features = {}

    # --- Time-based Features ---
    timestamp = log_entry.get("timestamp")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp)
        except ValueError:
            timestamp = datetime.datetime.now() # Fallback

    if isinstance(timestamp, datetime.datetime):
        features["login_hour"] = timestamp.hour
        features["day_of_week"] = timestamp.weekday() # Monday is 0, Sunday is 6
        features["is_weekend"] = 1 if timestamp.weekday() >= 5 else 0
        features["time_of_day_sin"] = datetime.datetime.now().hour / 23 # Placeholder for cyclical feature
        features["time_of_day_cos"] = datetime.datetime.now().minute / 59 # Placeholder for cyclical feature
    else:
        # Default values if timestamp is invalid
        features["login_hour"] = -1
        features["day_of_week"] = -1
        features["is_weekend"] = 0
        features["time_of_day_sin"] = 0
        features["time_of_day_cos"] = 0

    # --- User/Account-based Features ---
    # Assume 'metadata' might contain 'user' or 'is_admin'
    metadata = log_entry.get("metadata", {})
    user = metadata.get("user", "").lower()
    features["is_admin_account"] = 1 if user == "admin" or "root" in user else 0 # Simple heuristic
    features["failed_login_count_5min"] = 0 # Placeholder: This would require stateful tracking
    features["device_familiarity_score"] = 0 # Placeholder: Would need user-device history

    # --- Source/Network-based Features ---
    source = log_entry.get("source", "").lower()
    features["is_vpn_source"] = 1 if "vpn" in source else 0 # Simple heuristic
    features["geo_location_risk_score"] = 0 # Placeholder: Would need IP geo-location lookup

    # --- Event Type Features ---
    event_type = log_entry.get("event_type", "").lower()
    features["event_type_authentication"] = 1 if "auth" in event_type else 0
    features["event_type_file_access"] = 1 if "file" in event_type else 0
    features["event_type_process_exec"] = 1 if "process" in event_type or "exec" in event_type else 0
    features["event_type_privilege_escalation"] = 1 if "privilege" in event_type or "escalation" in event_type else 0

    # For demonstration, we'll ensure all features are numerical
    # In a real system, categorical features would need encoding (e.g., one-hot encoding)

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
