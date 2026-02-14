import requests
import datetime
import time
import json
import random
from faker import Faker

FASTAPI_URL = "https://soc-hackathon-backend.onrender.com"

fake = Faker()

# --- Configuration for log generation ---
NUM_LOGS_TO_GENERATE = 50
ANOMALY_RATIO = 0.2  # 20% of logs will be anomalous

# --- Expanded data for randomization ---
USER_TYPES = ["employee", "admin", "guest", "service_account"]
EVENT_TYPES = ["authentication", "process_execution", "network_connection", "file_access", "system_health"]
SOURCES = ["workstation-" + str(i).zfill(2) for i in range(1, 11)] + \
          ["server-linux-" + str(i).zfill(2) for i in range(1, 6)] + \
          ["server-windows-" + str(i).zfill(2) for i in range(1, 6)] + \
          ["firewall-" + str(i).zfill(2) for i in range(1, 3)] + \
          ["remote-vpn-user"]

def generate_random_ip(is_internal=True):
    if is_internal:
        return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
    else:
        return fake.ipv4_public()

def generate_normal_log():
    log = {
        "timestamp": fake.date_time_between(start_date="-1h", end_date="now").isoformat(),
        "source": random.choice(SOURCES),
        "event_type": random.choice(EVENT_TYPES),
        "metadata": {}
    }

    user = fake.user_name()
    ip_address = generate_random_ip()

    if log["event_type"] == "authentication":
        log["message"] = f"User {user} logged in successfully from {ip_address}"
        log["metadata"] = {"user": user, "ip_address": ip_address, "status": "success"}
    elif log["event_type"] == "process_execution":
        process = fake.file_name(category="application")
        log["message"] = f"Process {process} executed by user {user}"
        log["metadata"] = {"user": user, "process": process, "status": "success"}
    elif log["event_type"] == "network_connection":
        dest_ip = generate_random_ip(is_internal=False)
        port = random.choice([80, 443, 22, 3389])
        log["message"] = f"Allowed connection from {ip_address} to {dest_ip} on port {port}"
        log["metadata"] = {"src_ip": ip_address, "dest_ip": dest_ip, "port": port, "action": "allow"}
    elif log["event_type"] == "file_access":
        filename = fake.file_name()
        log["message"] = f"User {user} accessed file {filename}"
        log["metadata"] = {"user": user, "filename": filename, "action": random.choice(["read", "write"])}
    elif log["event_type"] == "system_health":
        log["message"] = f"System health check completed successfully on {log['source']}"
        log["metadata"] = {"status": "ok", "component": random.choice(["cpu", "memory", "disk"])}
    
    return log

def generate_anomalous_log():
    anomaly_type = random.choice([
        "admin_login_outside_hours", "failed_logins", "unusual_process",
        "remote_access_admin", "unexpected_network_conn"
    ])

    user = fake.user_name()
    admin_user = "admin" if random.random() < 0.7 else fake.user_name() # Mostly admin
    ip_address = fake.ipv4_public()
    internal_ip = generate_random_ip()

    log = {
        "timestamp": fake.date_time_between(start_date="-1h", end_date="now").isoformat(),
        "source": random.choice(SOURCES),
        "event_type": "authentication", # Default for many anomalies
        "metadata": {}
    }

    if anomaly_type == "admin_login_outside_hours":
        # Force a timestamp outside typical working hours (e.g., 2 AM)
        log["timestamp"] = fake.date_time_between(start_date="-1d", end_date="-1d").replace(hour=random.choice([0,1,2,3,4,5,6,22,23]), minute=random.randint(0,59)).isoformat()
        log["event_type"] = "authentication"
        log["message"] = f"User {admin_user} logged in outside business hours from {ip_address}"
        log["metadata"] = {"user": admin_user, "ip_address": ip_address, "status": "success"}
    elif anomaly_type == "failed_logins":
        failed_attempts = random.randint(5, 15)
        log["event_type"] = "authentication"
        log["message"] = f"User {user} failed {failed_attempts} login attempts from {ip_address}"
        log["metadata"] = {"user": user, "ip_address": ip_address, "status": "failed", "failed_attempts": failed_attempts}
    elif anomaly_type == "unusual_process":
        mal_process = random.choice(["powershell.exe -EncodedCommand ...", "nc.exe -lvp 4444", "mimikatz.exe"])
        log["event_type"] = "process_execution"
        log["message"] = f"Unusual process '{mal_process}' started on {log['source']}"
        log["metadata"] = {"user": user, "process": mal_process, "status": "executed"}
    elif anomaly_type == "remote_access_admin":
        log["event_type"] = "remote_access"
        log["message"] = f"Administrator {admin_user} accessed {log['source']} remotely from {ip_address}"
        log["metadata"] = {"user": admin_user, "ip_address": ip_address, "protocol": random.choice(["RDP", "SSH"])}
    elif anomaly_type == "unexpected_network_conn":
        dest_ip = fake.ipv4_public()
        port = random.choice([8080, 27017, 6379]) # Unusual ports
        log["event_type"] = "network_connection"
        log["message"] = f"Unexpected outbound connection from {log['source']} to {dest_ip} on port {port}"
        log["metadata"] = {"src_ip": internal_ip, "dest_ip": dest_ip, "port": port, "action": "allow"}

    return log

def send_log_to_fastapi(log_data: dict):
    """Sends a single log entry to the FastAPI /ingest-log endpoint."""
    try:
        if "timestamp" not in log_data:
            log_data["timestamp"] = datetime.datetime.now().isoformat()
        
        response = requests.post(f"{FASTAPI_URL}/ingest-log", json=log_data, timeout=5) # Added timeout
        response.raise_for_status()
        print(f"Successfully ingested log: {log_data.get('message', 'No message')} | Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error ingesting log: {log_data.get('message', 'No message')} | {e}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON response for log: {log_data.get('message', 'No message')}")

def train_model_on_fastapi():
    """Triggers the /train-model endpoint on FastAPI."""
    print("\nAttempting to train the anomaly detection model...")
    try:
        response = requests.post(f"{FASTAPI_URL}/train-model", timeout=10) # Added timeout
        response.raise_for_status()
        print(f"Model training triggered successfully: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error triggering model training: {e}")

def main(num_logs=NUM_LOGS_TO_GENERATE, anomaly_ratio=ANOMALY_RATIO):
    normal_logs_count = int(num_logs * (1 - anomaly_ratio))
    anomalous_logs_count = num_logs - normal_logs_count

    all_generated_logs = []
    for _ in range(normal_logs_count):
        all_generated_logs.append(generate_normal_log())
    for _ in range(anomalous_logs_count):
        all_generated_logs.append(generate_anomalous_log())

    random.shuffle(all_generated_logs) # Mix normal and anomalous logs

    print(f"--- Sending {num_logs} logs ({normal_logs_count} normal, {anomalous_logs_count} anomalous) ---")
    for i, log in enumerate(all_generated_logs):
        send_log_to_fastapi(log)
        time.sleep(0.2) # Small delay between logs
        if (i + 1) % 10 == 0:
            print(f"Sent {i + 1}/{num_logs} logs...")

    print("\nWaiting a few seconds before training model...")
    time.sleep(5) # Give backend time to process logs before training

    train_model_on_fastapi()

    print("\nLog ingestion and model training simulation complete.")
    print(f"You can now check your frontend dashboard at https://soc-hackathon-six.vercel.app")
    print(f"And FastAPI docs at {FASTAPI_URL}/docs")


if __name__ == "__main__":
    main()