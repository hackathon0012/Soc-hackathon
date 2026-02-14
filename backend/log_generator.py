import requests
import datetime
import time
import json

FASTAPI_URL = "https://soc-hackathon-backend.onrender.com"

# --- Define a set of "normal" log entries ---
NORMAL_LOGS = [
    {
        "source": "workstation-01",
        "event_type": "authentication",
        "message": "User alice logged in from office network",
        "metadata": {"user": "alice", "ip_address": "192.168.1.5"}
    },
    {
        "source": "server-linux",
        "event_type": "process_execution",
        "message": "Cron job ran successfully",
        "metadata": {"user": "root", "command": "/usr/bin/python cleanup.py"}
    },
    {
        "source": "firewall-01",
        "event_type": "network_connection",
        "message": "Allowed connection from 192.168.1.10 to 8.8.8.8 on port 443",
        "metadata": {"src_ip": "192.168.1.10", "dest_ip": "8.8.8.8", "port": 443, "action": "allow"}
    },
    {
        "source": "workstation-02",
        "event_type": "file_access",
        "message": "User bob accessed document 'report.docx'",
        "metadata": {"user": "bob", "filename": "report.docx", "action": "read"}
    },
    {
        "source": "server-windows",
        "event_type": "authentication",
        "message": "User charlie logged in remotely via RDP",
        "metadata": {"user": "charlie", "ip_address": "172.16.0.150", "protocol": "RDP"}
    },
    {
        "source": "workstation-01",
        "event_type": "authentication",
        "message": "User alice logged in from office network",
        "metadata": {"user": "alice", "ip_address": "192.168.1.5"}
    },
    {
        "source": "server-linux",
        "event_type": "process_execution",
        "message": "System health check completed",
        "metadata": {"user": "system", "command": "/usr/bin/healthcheck.sh"}
    },
    {
        "source": "firewall-01",
        "event_type": "network_connection",
        "message": "Allowed connection from 192.168.1.12 to 4.4.4.4 on port 53",
        "metadata": {"src_ip": "192.168.1.12", "dest_ip": "4.4.4.4", "port": 53, "action": "allow"}
    },
]

# --- Define a set of "anomalous" log entries ---
ANOMALOUS_LOGS = [
    {
        # Should trigger "Admin Login Outside Business Hours" rule (if timestamp is outside 8-18)
        "timestamp": (datetime.datetime.now().replace(hour=3, minute=15) - datetime.timedelta(days=1)).isoformat(), # Example: 3:15 AM yesterday
        "source": "remote-vpn-user",
        "event_type": "authentication",
        "message": "User admin logged in from unknown IP",
        "metadata": {"user": "admin", "ip_address": "203.0.113.100"}
    },
    {
        # Should trigger "Admin Login on Weekend" rule
        # Calculate next Saturday's date
        "timestamp": (datetime.datetime.now() + datetime.timedelta(days=(5 - datetime.datetime.now().weekday() + 7) % 7)).replace(hour=10, minute=0).isoformat(), # Example: Next Saturday 10:00 AM
        "source": "server-02",
        "event_type": "authentication",
        "message": "User admin logged into critical server during weekend",
        "metadata": {"user": "admin", "ip_address": "10.0.0.20"}
    },
    {
        "timestamp": (datetime.datetime.now().replace(hour=1, minute=0)).isoformat(), # Example: 1:00 AM
        "source": "workstation-03",
        "event_type": "process_execution",
        "message": "Unusual process 'powershell.exe -EncodedCommand ...' started",
        "metadata": {"user": "david", "command": "powershell.exe -EncodedCommand ..."}
    },
    {
        "timestamp": (datetime.datetime.now().replace(hour=23, minute=30) - datetime.timedelta(days=1)).isoformat(), # Example: 11:30 PM yesterday
        "source": "workstation-01",
        "event_type": "authentication",
        "message": "User alice failed 5 login attempts",
        "metadata": {"user": "alice", "ip_address": "192.168.1.5", "failed_attempts": 5}
    }
]

def send_log_to_fastapi(log_data: dict):
    """Sends a single log entry to the FastAPI /ingest-log endpoint."""
    try:
        # Add current timestamp if not explicitly provided
        if "timestamp" not in log_data:
            log_data["timestamp"] = datetime.datetime.now().isoformat()
        
        response = requests.post(f"{FASTAPI_URL}/ingest-log", json=log_data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Successfully ingested log: {log_data.get('message', 'No message')} | Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error ingesting log: {log_data.get('message', 'No message')} | {e}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON response for log: {log_data.get('message', 'No message')}")

def train_model_on_fastapi():
    """Triggers the /train-model endpoint on FastAPI."""
    print("\nAttempting to train the anomaly detection model...")
    try:
        response = requests.post(f"{FASTAPI_URL}/train-model")
        response.raise_for_status()
        print(f"Model training triggered successfully: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error triggering model training: {e}")

def main():
    print("--- Sending NORMAL logs ---")
    for log in NORMAL_LOGS:
        send_log_to_fastapi(log)
        time.sleep(0.5) # Small delay

    # Give a moment for logs to be processed in FastAPI before training
    print("\nWaiting a few seconds before training model...")
    time.sleep(3)

    train_model_on_fastapi()

    print("\n--- Sending ANOMALOUS logs ---")
    for log in ANOMALOUS_LOGS:
        send_log_to_fastapi(log)
        time.sleep(0.5) # Small delay

    print("\nLog ingestion and model training simulation complete.")
    print(f"You can now check your frontend dashboard at {FASTAPI_URL.replace('http://127.0.0.1:8000', 'http://localhost:5173')}")
    print(f"And FastAPI docs at {FASTAPI_URL}/docs")


if __name__ == "__main__":
    main()