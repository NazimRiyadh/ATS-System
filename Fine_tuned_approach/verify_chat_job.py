"""
Test the /chat_job endpoint with mix mode.
This will test the automatic fallback from mix to naive mode.
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_analyze_job():
    """Step 1: Analyze a job to create a shortlist"""
    print("=" * 70)
    print("Step 1: Analyzing job to create shortlist")
    print("=" * 70)
    
    url = f"{API_BASE}/analyze_job"
    payload = {
        "job_id": "test_mix_mode_001",
        "query": "Python developer with machine learning and NLP experience",
        "top_k": 5
    }
    
    print(f"\nPOST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_chat_job_mix_mode():
    """Step 2: Test chat_job with mix mode (should fallback to naive)"""
    print("\n" + "=" * 70)
    print("Step 2: Testing /chat_job with mix mode")
    print("=" * 70)
    
    url = f"{API_BASE}/chat_job"
    payload = {
        "job_id": "test_mix_mode_001",
        "message": "Who has the best Python and machine learning experience?",
        "mode": "mix"  # This should attempt mix mode, then fallback to naive
    }
    
    print(f"\nPOST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    return result

def test_chat_job_naive_mode():
    """Step 3: Test chat_job with naive mode directly"""
    print("\n" + "=" * 70)
    print("Step 3: Testing /chat_job with naive mode")
    print("=" * 70)
    
    url = f"{API_BASE}/chat_job"
    payload = {
        "job_id": "test_mix_mode_001",
        "message": "List all candidates and their skills",
        "mode": "naive"  # Direct naive mode
    }
    
    print(f"\nPOST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload)
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    return result

if __name__ == "__main__":
    try:
        # Test the full workflow
        analyze_result = test_analyze_job()
        
        if analyze_result.get("candidates_found", 0) > 0:
            # Test mix mode (with fallback)
            mix_result = test_chat_job_mix_mode()
            
            # Test naive mode directly
            naive_result = test_chat_job_naive_mode()
            
            print("\n" + "=" * 70)
            print("✅ All tests completed successfully!")
            print("=" * 70)
        else:
            print("\n⚠️  No candidates found. Check if data was ingested properly.")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API at http://localhost:8000")
        print("   Make sure the API is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
