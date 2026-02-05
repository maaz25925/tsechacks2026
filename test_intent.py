#!/usr/bin/env python3
import requests
import json

url = "http://127.0.0.1:8000/milestones/intent"
payload = {
    "amount": 50,
    "currency": "USD",
    "description": "test",
    "metadata": {"session_id": "test_session"}
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
