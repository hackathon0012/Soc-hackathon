from typing import Dict, Any, List, Optional

# Define a list of simple detection rules
# Each rule has:
# - name: A unique name for the rule
# - conditions: A dictionary or list of conditions to check against features.
#               For simplicity, conditions are key-value checks or simple comparisons.
# - severity: The severity level if the rule matches ("Low", "Medium", "High", "Critical")

DETECTION_RULES = [
    {
        "name": "Admin Login Outside Business Hours",
        "conditions": [
            {"feature": "is_admin_account", "operator": "==", "value": 1},
            {"feature": "login_hour", "operator": "not_in", "value": list(range(8, 18))}, # 8 AM to 5 PM
            {"feature": "is_weekend", "operator": "==", "value": 0}
        ],
        "severity": "High",
        "description": "An administrative account logged in outside typical 8 AM - 5 PM business hours on a weekday."
    },
    {
        "name": "Admin Login on Weekend",
        "conditions": [
            {"feature": "is_admin_account", "operator": "==", "value": 1},
            {"feature": "is_weekend", "operator": "==", "value": 1}
        ],
        "severity": "Critical",
        "description": "An administrative account logged in during the weekend."
    },
    {
        "name": "Unusual Login Hour (Non-Admin)",
        "conditions": [
            {"feature": "is_admin_account", "operator": "==", "value": 0},
            {"feature": "login_hour", "operator": "not_in", "value": list(range(7, 20))}, # 7 AM to 7 PM
            {"feature": "is_weekend", "operator": "==", "value": 0}
        ],
        "severity": "Medium",
        "description": "A non-administrative account logged in outside typical 7 AM - 7 PM business hours on a weekday."
    },
    {
        "name": "Process Execution by Admin on Weekend",
        "conditions": [
            {"feature": "is_admin_account", "operator": "==", "value": 1},
            {"feature": "event_type_process_exec", "operator": "==", "value": 1},
            {"feature": "is_weekend", "operator": "==", "value": 1}
        ],
        "severity": "High",
        "description": "An administrative account executed a process during the weekend."
    }
    # Add more rules as needed for other event types, failed logins, etc.
]

# Mapping severity to a numerical score for risk calculation
SEVERITY_SCORES = {
    "Low": 20,
    "Medium": 50,
    "High": 80,
    "Critical": 100
}

def apply_rules(features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Applies defined rules to a set of extracted features.

    Args:
        features: A dictionary of extracted numerical features for a log entry.

    Returns:
        A list of dictionaries, where each dictionary represents a matched rule.
        Returns an empty list if no rules match.
    """
    matched_rules = []
    for rule in DETECTION_RULES:
        match = True
        for condition in rule["conditions"]:
            feature_value = features.get(condition["feature"])

            # Handle missing features in rules (e.g., if feature_engineering changes)
            if feature_value is None:
                match = False
                break

            operator = condition["operator"]
            value = condition["value"]

            if operator == "==":
                if feature_value != value:
                    match = False
                    break
            elif operator == "!=":
                if feature_value == value:
                    match = False
                    break
            elif operator == ">":
                if not (feature_value > value):
                    match = False
                    break
            elif operator == "<":
                if not (feature_value < value):
                    match = False
                    break
            elif operator == "in":
                if feature_value not in value:
                    match = False
                    break
            elif operator == "not_in":
                if feature_value in value:
                    match = False
                    break
            # Add more operators as needed (e.g., >=, <=)
            else:
                # Unknown operator, treat as no match
                match = False
                break

        if match:
            matched_rules.append({
                "name": rule["name"],
                "severity": rule["severity"],
                "description": rule["description"],
                "score": SEVERITY_SCORES.get(rule["severity"], 0)
            })
    return matched_rules

# Example Usage
if __name__ == "__main__":
    test_features_admin_weekend = {
        "login_hour": 3, "day_of_week": 6, "is_admin_account": 1, "is_vpn_source": 0,
        "event_type_authentication": 1, "event_type_file_access": 0,
        "event_type_process_exec": 0, "event_type_privilege_escalation": 0,
        "is_weekend":1, "time_of_day_sin":0.1, "time_of_day_cos":0.1,
        "failed_login_count_5min":0, "device_familiarity_score":0, "geo_location_risk_score":0
    }
    
    test_features_normal = {
        "login_hour": 9, "day_of_week": 1, "is_admin_account": 0, "is_vpn_source": 0,
        "event_type_authentication": 1, "event_type_file_access": 0,
        "event_type_process_exec": 0, "event_type_privilege_escalation": 0,
        "is_weekend":0, "time_of_day_sin":0.5, "time_of_day_cos":0.5,
        "failed_login_count_5min":0, "device_familiarity_score":0, "geo_location_risk_score":0
    }

    print("Matching rules for admin weekend login:")
    matched = apply_rules(test_features_admin_weekend)
    for r in matched:
        print(f"- {r['name']} ({r['severity']})")

    print("\nMatching rules for normal login:")
    matched = apply_rules(test_features_normal)
    if not matched:
        print("No rules matched.")