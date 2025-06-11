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

def get_next_file_number():
    """Get the next file number for the current date"""
    today = datetime.now().strftime("%Y-%m-%d")
    pattern = f"/var/log/app/my-logs-{today}-*.log"
    existing_files = glob.glob(pattern)
    if not existing_files:
        return 1
    numbers = [int(f.split('-')[-1].split('.')[0]) for f in existing_files]
    return max(numbers) + 1 if numbers else 1

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

def write_logs_bulk():
    """Write logs in bulk to a new file"""
    today = datetime.now().strftime("%Y-%m-%d")
    file_number = get_next_file_number()
    filename = f"/var/log/app/my-logs-{today}-{file_number}.log"
    filename_service1 = f"/var/log/app/service1-logs-{today}-{file_number}.log"
    
    # Generate and write logs in bulk
    logs = []
    logs_service1 = []
    for _ in range(100):  # Generate 100 logs at once
        logs.append(generate_log() if random.random() < 1.0 else generate_bad_log())
        logs_service1.append(generate_service1_log())


    print(f"logs: {logs}")
    print(f"logs_service1: {logs_service1}")
    
    with open(filename, 'w') as f:
        f.write('\n'.join(logs))
    with open(filename_service1, 'w') as f:
        f.write('\n'.join(logs_service1))

    print(f"Written {len(logs)} logs to {filename}")
    print(f"Written {len(logs_service1)} logs to {filename_service1}")

def main():
    """Main function to generate logs every 5 seconds"""
    while True:
        write_logs_bulk()
        time.sleep(15)  # Wait for 5 seconds

if __name__ == "__main__":
    main() 