#!/usr/bin/env python3
"""
API Test Script - Testet alle Backend-Endpoints
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_status():
    """Test Status Endpoint"""
    print("[TEST] Status endpoint...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    return response.status_code == 200

def test_start_interview():
    """Test Interview Start"""
    print("\n[TEST] Start interview...")
    data = {
        "candidate_phone": "+49987654321",
        "position": "Senior Software Engineer"
    }
    response = requests.post(f"{BASE_URL}/start-interview", json=data)
    print(f"  Status: {response.status_code}")
    result = response.json()
    print(f"  Response: {result}")
    
    if response.status_code == 200:
        return result.get("call_id")
    return None

def test_interviews_list():
    """Test Interviews List"""
    print("\n[TEST] Get interviews list...")
    response = requests.get(f"{BASE_URL}/interviews")
    print(f"  Status: {response.status_code}")
    result = response.json()
    print(f"  Found {len(result)} interviews")
    for interview in result:
        print(f"    ID: {interview['id']}, Phone: {interview['candidate_phone']}, Status: {interview['status']}")
    return response.status_code == 200

def test_complete_interview(call_id):
    """Test Interview Completion (Demo)"""
    print(f"\n[TEST] Complete interview {call_id}...")
    data = {"call_id": call_id}
    response = requests.post(f"{BASE_URL}/demo/complete-interview", json=data)
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=== AI Interview Agent - API Tests ===\n")
    
    try:
        # Test 1: Status
        if not test_status():
            print("[ERROR] Status test failed")
            return
        
        # Test 2: Start Interview
        call_id = test_start_interview()
        if not call_id:
            print("[ERROR] Start interview test failed")
            return
        
        # Test 3: List Interviews
        if not test_interviews_list():
            print("[ERROR] Interviews list test failed")
            return
        
        # Test 4: Complete Interview
        if not test_complete_interview(call_id):
            print("[ERROR] Complete interview test failed")
            return
        
        # Wait for processing
        print("\n[INFO] Waiting for interview processing...")
        time.sleep(3)
        
        # Test 5: Check final state
        print("\n[TEST] Final interviews state...")
        response = requests.get(f"{BASE_URL}/interviews")
        result = response.json()
        
        completed_interview = None
        for interview in result:
            if interview.get('status') == 'completed':
                completed_interview = interview
                break
        
        if completed_interview:
            print("[SUCCESS] Interview completed successfully!")
            print(f"  Score: {completed_interview.get('score')}")
            print(f"  Duration: {completed_interview.get('completed_at')}")
        else:
            print("[WARNING] No completed interview found")
        
        print("\n[SUCCESS] All API tests passed!")
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to backend. Make sure the server is running:")
        print("  python app_flask.py")
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")

if __name__ == "__main__":
    main()