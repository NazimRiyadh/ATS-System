import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_search():
    print("Testing Search...")
    payload = {
        "query": "Python Developer",
        "filters": {"min_years_experience": 2}
    }
    response = requests.post(f"{BASE_URL}/search", json=payload)
    if response.status_code == 200:
        results = response.json()
        print(f"✅ Search successful. Found {len(results)} candidates.")
        if results:
            return results[0]['candidate_id']
    else:
        print(f"❌ Search failed: {response.text}")
    return None

def test_feedback(candidate_id):
    print("\nTesting Feedback...")
    payload = {
        "candidate_id": candidate_id,
        "query": "Python Developer",
        "action": "like"
    }
    response = requests.post(f"{BASE_URL}/feedback", json=payload)
    if response.status_code == 200:
        print("✅ Feedback recorded successfully.")
    else:
        print(f"❌ Feedback failed: {response.text}")

def test_chat(candidate_id):
    print("\nTesting Chat...")
    payload = {
        "candidate_id": candidate_id,
        "message": "What is this candidate's experience with Python?"
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    if response.status_code == 200:
        print(f"✅ Chat response: {response.json()['response']}")
    else:
        print(f"❌ Chat failed: {response.text}")

if __name__ == "__main__":
    candidate_id = test_search()
    if candidate_id:
        test_feedback(candidate_id)
        test_chat(candidate_id)
