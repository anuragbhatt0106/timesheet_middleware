#!/usr/bin/env python3

import requests
import sys
import os

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_validate_endpoint_no_file():
    """Test validation endpoint without file"""
    try:
        response = requests.post('http://localhost:5000/validate-timesheet')
        print(f"No file test: {response.status_code} - {response.json()}")
        return response.status_code == 400
    except Exception as e:
        print(f"No file test failed: {e}")
        return False

def test_validate_endpoint_with_sample():
    """Test validation endpoint with sample data"""
    try:
        # Create a simple text file to test
        with open('/tmp/test_timesheet.txt', 'w') as f:
            f.write("Total Hours: 8.5")
        
        with open('/tmp/test_timesheet.txt', 'rb') as f:
            files = {'file': f}
            data = {'claimed_hours': '8.5'}
            response = requests.post('http://localhost:5000/validate-timesheet', files=files, data=data)
            print(f"Sample validation: {response.status_code} - {response.json()}")
        
        os.unlink('/tmp/test_timesheet.txt')
        return True
    except Exception as e:
        print(f"Sample validation failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Timesheet API...")
    print("Note: Make sure the Flask app is running on localhost:5000")
    print()
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("No File Error", test_validate_endpoint_no_file),
        ("Sample Validation", test_validate_endpoint_with_sample)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
        print(f"{test_name}: {'PASS' if result else 'FAIL'}")
        print()
    
    print("Test Summary:")
    for test_name, result in results:
        print(f"  {test_name}: {'PASS' if result else 'FAIL'}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")