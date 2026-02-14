import requests
import datetime
import time
import json
import os
import sys

# Try to import WMI for Windows event log access
try:
    import WMI
    # Make sure pywintypes is available, as WMI depends on it
    import win32evtlog
    import win32security
    import win32api
    import win32con
except ImportError:
    print("WMI module not found. This agent requires WMI for Windows Event Log access.")
    print("Please install it using: pip install python-wmi pywin32")
    sys.exit(1)

FASTAPI_URL = "http://127.0.0.1:8000" # This will need to be configured for deployment
POLLING_INTERVAL_SECONDS = 5 # How often to check for new logs

# Placeholder for last event log read timestamp/ID
# In a real agent, this would be persisted to a file
LAST_EVENT_RECORD_ID = {} # {log_name: last_id_read}

def get_event_log_sources():
    """Returns a list of common Windows Event Log sources to monitor."""
    return ["Security", "System", "Application"] # Add more as needed

def read_windows_event_logs(log_name: str, last_record_id: int = 0) -> list:
    """Reads new events from a specified Windows Event Log."""
    events = []
    handle = None
    try:
        handle = win32evtlog.OpenEventLog(None, log_name)
        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        
        # Read all events first to find the latest, then read from the last_record_id
        # or read everything if starting fresh.
        # For simplicity, we'll read up to a certain limit if last_record_id is 0.
        # A more robust solution would iterate until last_record_id is reached.
        total_records = win32evtlog.GetNumberOfEventLogRecords(handle)
        
        # Determine starting record ID
        start_record_id = last_record_id
        if last_record_id == 0:
            # If starting fresh, read last N records for initial population
            # or simply read from the latest available if we're not persisting.
            # For now, let's read the latest 100 events if no last_record_id.
            read_count = min(total_records, 100) # Read max 100 events
            if total_records > read_count:
                start_record_id = total_records - read_count

        # Read events
        # Note: win32evtlog.ReadEventLog reads in reverse order usually with FORWARDS_READ | SEQUENTIAL_READ
        # So we need to reverse the list.
        # This is a bit tricky with win32evtlog; a simpler approach for new events is to query by time.
        # For a basic example, let's just read a batch and keep track of the max record ID.

        # A more robust way to get new events would be using WMI directly or querying by time.
        # For simplicity here, we'll just read from the *end* of the log.
        # We'll rely on our LAST_EVENT_RECORD_ID to filter what's truly new.

        # For this prototype, let's simplify reading from the end, then filtering by RecordId.
        # This is a less efficient but simpler way for a demo.
        raw_events = win32evtlog.ReadEventLog(handle, flags, start_record_id)
        
        current_max_record_id = last_record_id

        if raw_events:
            for event in raw_events:
                if event.RecordNumber > last_record_id:
                    event_data = {
                        "timestamp": event.TimeGenerated.Format('%Y-%m-%dT%H:%M:%S'),
                        "source": f"Windows-{log_name}",
                        "event_type": f"WinEvt-{event.EventType}", # EventType is numeric, map later
                        "message": str(event.StringInserts), # Might be list of strings, convert
                        "metadata": {
                            "EventID": event.EventID,
                            "RecordNumber": event.RecordNumber,
                            "ComputerName": event.ComputerName,
                            "User": win32security.LookupSidName(None, event.Sid)[0] if event.Sid else None,
                            "Category": event.EventCategory,
                            "SourceName": event.SourceName,
                            "EventTypeName": win32evtlog.EvtFormatMessage(handle, event.EventID, event.EventType, event.StringInserts) # More descriptive
                        }
                    }
                    events.append(event_data)
                    if event.RecordNumber > current_max_record_id:
                        current_max_record_id = event.RecordNumber
        
        return events, current_max_record_id

    except Exception as e:
        print(f"Error reading Windows Event Log '{log_name}': {e}")
        return [], last_record_id
    finally:
        if handle:
            win32evtlog.CloseEventLog(handle)


def send_log_to_fastapi(log_data: dict):
    """Sends a single log entry to the FastAPI /ingest-log endpoint."""
    try:
        if "timestamp" not in log_data:
            log_data["timestamp"] = datetime.datetime.now().isoformat()
        
        response = requests.post(f"{FASTAPI_URL}/ingest-log", json=log_data)
        response.raise_for_status()
        print(f"Agent: Successfully ingested log (ID: {response.json().get('log_id', 'N/A')}) from {log_data.get('source')} | Type: {log_data.get('event_type')}")
    except requests.exceptions.RequestException as e:
        print(f"Agent: Error ingesting log: {e}")
    except json.JSONDecodeError:
        print(f"Agent: Error decoding JSON response.")

def main():
    print("AI-SOC Lite Agent started. Monitoring Windows Event Logs...")
    
    # Load last recorded IDs from a persistence file if it exists
    persistence_file = "agent_state.json"
    if os.path.exists(persistence_file):
        with open(persistence_file, 'r') as f:
            global LAST_EVENT_RECORD_ID
            LAST_EVENT_RECORD_ID = json.load(f)
            print(f"Agent: Loaded last recorded event IDs: {LAST_EVENT_RECORD_ID}")

    while True:
        for log_name in get_event_log_sources():
            last_id_for_source = LAST_EVENT_RECORD_ID.get(log_name, 0)
            
            new_events, current_max_id = read_windows_event_logs(log_name, last_id_for_source)
            
            if new_events:
                print(f"Agent: Found {len(new_events)} new events in {log_name}.")
                for event in new_events:
                    send_log_to_fastapi(event)
                    time.sleep(0.1) # Small delay to not overwhelm the backend
                
                # Update last recorded ID if new events were processed
                if current_max_id > last_id_for_source:
                    LAST_EVENT_RECORD_ID[log_name] = current_max_id
                    print(f"Agent: Updated last recorded ID for {log_name} to {current_max_id}")
                    
                    # Persist the last recorded ID
                    with open(persistence_file, 'w') as f:
                        json.dump(LAST_EVENT_RECORD_ID, f)
            else:
                print(f"Agent: No new events in {log_name}.")
        
        time.sleep(POLLING_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
