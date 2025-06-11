import logging
import random
import time
import json
from datetime import datetime
import os
import glob
import uuid

# Create logs directory if it doesn't exist
os.makedirs('/var/log/app', exist_ok=True)

def generate_log():
    """Generate a single log entry in JSON format"""
    log_data = {
        "@timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user_id": random.randint(1, 1000),
        "action": random.choice(["login", "logout", "view", "edit", "delete"]),
        "status": random.choice(["success", "error", "warning"]),
        "response_time": round(random.uniform(0.1, 2.0), 3)
    }
    return json.dumps(log_data)

def generate_bad_log():
    log_data = {
        "@timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user_id": random.choice(["david", "ben", "fisher"]),
        "action": random.choice(["login", "logout", "view", "edit", "delete"]),
        "status": random.choice(["success", "error", "warning"]),
        "response_time": round(random.uniform(0.1, 2.0), 3)
    }
    return json.dumps(log_data)

def generate_service1_log():
    log_data = {
        "@timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user_id": random.randint(1, 1000),
        "action": random.choice(["login", "logout", "view", "edit", "delete"]),
        "status": random.choice(["success", "error", "warning"]),
        "response_time": round(random.uniform(0.1, 2.0), 3),
        "hard_coded_source_file": "service1"
    }   
    return json.dumps(log_data)

def generate_service2_log():
    """Generate a service2 log with log_type field"""
    log_type = random.choice([1, 2])
    log_data = {
        "@timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user_id": random.randint(1, 1000),
        "action": random.choice(["process", "validate", "transform", "export"]),
        "status": random.choice(["success", "error", "warning"]),
        "response_time": round(random.uniform(0.1, 2.0), 3),
        "log_type": log_type,
        "service_name": "service2"
    }
    return json.dumps(log_data)

def write_logs_bulk():
    """Write logs in bulk to a new file for each log type, with a UUID in the filename."""
    today = datetime.now().strftime("%Y-%m-%d")
    file_uuid_mylogs = uuid.uuid4()
    file_uuid_service1 = uuid.uuid4()
    file_uuid_service2 = uuid.uuid4()

    filename = f"/var/log/app/my-logs-{today}-{file_uuid_mylogs}.log"
    filename_service1 = f"/var/log/app/service1-logs-{today}-{file_uuid_service1}.log"
    filename_service2 = f"/var/log/app/service2-logs-{today}-{file_uuid_service2}.log"

    # Generate and write logs in bulk
    logs = []
    logs_service1 = []
    logs_service2 = []
    for _ in range(100):  # Generate 100 logs at once
        logs.append(generate_log())
        logs_service1.append(generate_service1_log())
        logs_service2.append(generate_service2_log())

    with open(filename, 'w') as f:
        f.write('\n'.join(logs) + '\n')
    with open(filename_service1, 'w') as f:
        f.write('\n'.join(logs_service1) + '\n')
    with open(filename_service2, 'w') as f:
        f.write('\n'.join(logs_service2) + '\n')

    print(f"Written {len(logs)} logs to {filename}")
    print(f"Written {len(logs_service1)} logs to {filename_service1}")
    print(f"Written {len(logs_service2)} logs to {filename_service2}")

def main():
    """Main function to generate logs every 5 seconds"""
    while True:
        write_logs_bulk()
        time.sleep(15)  # Wait for 15 seconds

if __name__ == "__main__":
    main() 