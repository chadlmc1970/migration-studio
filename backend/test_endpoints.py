#!/usr/bin/env python3
"""
Test script for the Migration Studio API endpoints

Usage:
    python test_endpoints.py
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api"


def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_state():
    """Test state endpoint"""
    print("Testing /api/state...")
    response = requests.get(f"{BASE_URL}/state")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_universes():
    """Test universes list endpoint"""
    print("Testing /api/universes...")
    response = requests.get(f"{BASE_URL}/universes")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_events():
    """Test events endpoint"""
    print("Testing /api/events...")
    response = requests.get(f"{BASE_URL}/events?limit=10")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_upload():
    """Test file upload endpoint"""
    print("Testing POST /api/upload...")

    # Create a sample .unv file for testing
    test_file_path = Path("/tmp/test_universe.unv")
    test_file_path.write_text("Sample universe content")

    with open(test_file_path, "rb") as f:
        files = {"file": ("test_universe.unv", f, "application/octet-stream")}
        response = requests.post(f"{BASE_URL}/upload", files=files)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    # Clean up
    test_file_path.unlink()


def test_reports(universe_id: str = "sales_universe"):
    """Test reports endpoint"""
    print(f"Testing GET /api/universes/{universe_id}/reports...")
    response = requests.get(f"{BASE_URL}/universes/{universe_id}/reports")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    else:
        print(f"Error: {response.text}\n")


def test_download(universe_id: str = "sales_universe", artifact: str = "sac/model.json"):
    """Test download endpoint"""
    print(f"Testing GET /api/universes/{universe_id}/download?artifact={artifact}...")
    response = requests.get(f"{BASE_URL}/universes/{universe_id}/download", params={"artifact": artifact})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content (first 200 chars): {response.text[:200]}...\n")
    else:
        print(f"Error: {response.text}\n")


def main():
    print("=" * 60)
    print("Universe Migration Studio API - Endpoint Tests")
    print("=" * 60 + "\n")

    # Test existing endpoints
    test_health()
    test_state()
    test_universes()
    test_events()

    print("\n" + "=" * 60)
    print("Testing NEW endpoints")
    print("=" * 60 + "\n")

    # Test new endpoints
    test_upload()
    test_reports()
    test_download()

    print("\nNote: To test POST /api/run, execute:")
    print("  curl -X POST http://localhost:8000/api/run")
    print("  (This will run the full pipeline which may take several minutes)")


if __name__ == "__main__":
    main()
