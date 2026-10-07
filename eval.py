import requests
import json
import sys
import time

def run_evals(service_url):
    print(f"Starting evaluation against {service_url}...\n")
    
    try:
        with open("data/conversations.json", "r", encoding="utf-8") as f:
            conversations = json.load(f)
    except FileNotFoundError:
        print("Error: data/conversations.json not found. Please ensure it exists.")
        sys.exit(1)

    for i, test_case in enumerate(conversations):
        rider_id = test_case.get("rider_id", f"eval_rider_{i}")
        scenario = test_case.get("scenario", "Unknown scenario")
        turns = test_case.get("turns", [])
        
        print(f"--- Test Case {i+1}: Rider {rider_id} | Scenario: {scenario} ---")
        
        for turn in turns:
            if turn.get("from") == "rider":
                payload = {
                    "message_id": turn.get("message_id", f"msg_{int(time.time())}"),
                    "rider_id": rider_id,
                    "text": turn.get("text", ""),
                    "received_at": turn.get("received_at", time.strftime("%Y-%m-%dT%H:%M:%S+05:30"))
                }
                
                print(f"Rider: {payload['text']}")
                try:
                    response = requests.post(f"{service_url}/messages", json=payload)
                    if response.status_code == 200:
                        print(f"Agent (Actual):   {response.json().get('reply')}")
                    else:
                        print(f"Server Error {response.status_code}: {response.text}")
                except Exception as e:
                    print(f"Connection Failed: {e}")
                
                # Slow down the loop to avoid hitting API rate limits
                time.sleep(8) 
                
            elif turn.get("from") == "agent":
                print(f"Agent (Expected): {turn.get('example')}\n")
                
        print("-" * 60 + "\n")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    run_evals(url)