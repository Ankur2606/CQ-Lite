"""
Test script for CQ Lite API endpoints
"""

import requests
import json
import time
import os
from pathlib import Path
import sys

# Define the API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health check endpoint"""
    print("\n📋 Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        print("✅ Health check endpoint is responding")
        print(f"Status: {response.json()['status']}")
        print("Services status:")
        for service, status in response.json()['services'].items():
            status_icon = "✅" if status else "❌"
            print(f"  - {service}: {status_icon}")
    else:
        print(f"❌ Health check failed with status code {response.status_code}")
        print(response.text)
    return response.status_code == 200

def test_root():
    """Test the root endpoint"""
    print("\n📋 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ Root endpoint is responding")
        print(f"API name: {response.json()['name']}")
        print(f"API version: {response.json()['version']}")
    else:
        print(f"❌ Root endpoint failed with status code {response.status_code}")
        print(response.text)
    return response.status_code == 200

def test_github_analyze():
    """Test the GitHub repository analysis endpoint"""
    print("\n📋 Testing GitHub repository analysis endpoint...")
    
    # Debug available routes
    print("DEBUG - Testing routes:")
    payload = {
        "repo_url": "https://github.com/Ankur2606/CQ-Lite",
        "service": "nebius",  # Using Nebius for faster results
        "include_notion": False,
        "max_files": 6,  # Reduced to 2 files for faster processing
        "include_patterns": ["*.py"]  # Focus only on Python files
    }
    
    endpoint = f"{BASE_URL}/api/analyze/github"
    print(f"Sending request to: {endpoint}")
    print(f"Payload: {json.dumps(payload)}")
    
    response = requests.post(endpoint, json=payload)
    if response.status_code == 200:
        print("✅ GitHub analysis endpoint is responding")
        print(f"Job ID: {response.json()['job_id']}")
        print(f"Status: {response.json()['status']}")
        print(f"Created at: {response.json().get('created_at', 'N/A')}")
        return response.json()['job_id']
    else:
        print(f"❌ GitHub analysis endpoint failed with status code {response.status_code}")
        print(response.text)
        return None

def test_status(job_id):
    """Test the analysis status endpoint"""
    print(f"\n📋 Testing analysis status endpoint for job {job_id}...")
    
    response = requests.get(f"{BASE_URL}/api/status/{job_id}")
    if response.status_code == 200:
        print("✅ Status endpoint is responding")
        print(f"Status: {response.json()['status']}")
        print(f"Progress: {response.json().get('progress', 'N/A')}%")
        # Message field might not exist in the response
        if 'message' in response.json():
            print(f"Message: {response.json()['message']}")
            
        # Print any additional information that might be helpful for debugging
        if response.json()['status'] == "failed":
            print(f"Error: {response.json().get('error', 'Unknown error')}")
        
        return response.json()['status']
    else:
        print(f"❌ Status endpoint failed with status code {response.status_code}")
        print(response.text)
        return None

def test_graph(job_id):
    """Test the dependency graph endpoint"""
    print(f"\n📋 Testing dependency graph endpoint for job {job_id}...")
    
    response = requests.get(f"{BASE_URL}/api/graph/{job_id}")
    if response.status_code == 200:
        print("✅ Graph endpoint is responding")
        graph_data = response.json()
        nodes = graph_data.get('dependency_graph', {}).get('nodes', [])
        edges = graph_data.get('dependency_graph', {}).get('links', [])  # Changed from 'edges' to 'links'
        
        print(f"Number of nodes: {len(nodes)}")
        print(f"Number of edges: {len(edges)}")
        
        # Print sample nodes if available
        if nodes:
            print("\nSample nodes:")
            for node in nodes[:5]:  # Show first 5 nodes
                print(f"  - {node.get('id', 'unknown')}: {node.get('group', 'no group')}")
                
        # Print sample edges if available
        if edges:
            print("\nSample edges:")
            for edge in edges[:5]:  # Show first 5 edges
                print(f"  - {edge.get('source', '?')} → {edge.get('target', '?')}")
        
        return True
    else:
        print(f"❌ Graph endpoint failed with status code {response.status_code}")
        print(f"Error: {response.text}")
        # Try to parse the error response if it's JSON
        try:
            error_data = response.json()
            if 'detail' in error_data:
                print(f"Detail: {error_data['detail']}")
        except:
            pass
        return False

def test_report(job_id):
    """Test the report generation endpoint"""
    print(f"\n📋 Testing report generation endpoint for job {job_id}...")
    
    # Test different report formats
    formats = ["json", "html", "md"]
    success = True
    
    for fmt in formats:
        payload = {
            "job_id": job_id,
            "format": fmt
        }
        
        print(f"Testing '{fmt}' format...")
        response = requests.post(f"{BASE_URL}/api/report", json=payload)
        
        if response.status_code == 200:
            print(f"✅ Report endpoint is responding for {fmt} format")
            
            # For JSON format, we can check the content
            if fmt == "json":
                try:
                    json_data = response.json()
                    print(f"  - Retrieved JSON report with {len(json_data.keys())} keys")
                except Exception as e:
                    print(f"  - Failed to parse JSON response: {str(e)}")
            
            # For HTML, just check that it starts with <!DOCTYPE html>
            elif fmt == "html":
                if response.text.strip().startswith("<!DOCTYPE html>"):
                    print("  - Retrieved HTML report")
                else:
                    print("  - Response doesn't look like HTML")
                    
            # For Markdown, check that it starts with # Code Analysis Report
            elif fmt == "md":
                if "# Code Analysis Report" in response.text:
                    print("  - Retrieved Markdown report")
                    print(f"/n/n{response.text[:500]}/n/n")  # Print first 500 chars
                else:
                    print("  - Response doesn't look like Markdown")
        else:
            print(f"❌ Report endpoint failed for {fmt} format with status code {response.status_code}")
            print(response.text)
            success = False
    
    return success

def test_file_upload():
    """Test the file upload endpoint"""
    print("\n📋 Testing file upload endpoint...")
    
    # Create a simple test file
    test_file_path = Path("test_upload.py")
    with open(test_file_path, "w") as f:
        f.write('print("Hello from test file")')
    
    try:
        # Open file and specify it as a list as the API expects
        with open(test_file_path, 'rb') as f:
            files = [('files', (test_file_path.name, f, 'text/plain'))]
            
            # The correct endpoint is /api/analyze/upload
            endpoint = f"{BASE_URL}/api/analyze/upload"
            print(f"Sending upload request to: {endpoint}")
            response = requests.post(endpoint, files=files)
        
        if response.status_code == 200:
            print("✅ File upload endpoint is responding")
            print(f"Job ID: {response.json()['job_id']}")
            print(f"Status: {response.json()['status']}")
            print(f"Created at: {response.json().get('created_at', 'N/A')}")
            return response.json()['job_id']
        else:
            print(f"❌ File upload endpoint failed with status code {response.status_code}")
            print(response.text)
            return None
    finally:
        # Clean up test file
        try:
            if test_file_path.exists():
                # Properly close file handles before attempting to delete
                import gc
                import time
                gc.collect()  # Force garbage collection to release file handles
                time.sleep(0.5)  # Give the OS a moment to release locks
                test_file_path.unlink()
        except Exception as e:
            print(f"Warning: Could not delete test file: {e}")
            # If we can't delete it now, mark for deletion on exit
            import atexit
            atexit.register(lambda: test_file_path.unlink(missing_ok=True))

def get_full_job_details(job_id):
    """Get detailed information about a job"""
    print(f"\n📊 Getting detailed job information for {job_id}...")
    
    # First check the status to determine if we should try the graph endpoint
    status_response = requests.get(f"{BASE_URL}/api/status/{job_id}")
    
    results = {}
    if status_response.status_code == 200:
        status_data = status_response.json()
        results["status"] = status_data
        print(f"✅ Retrieved data from status endpoint")
        
        # Only try to get graph data if the job completed successfully
        if status_data.get("status") == "completed":
            try:
                graph_response = requests.get(f"{BASE_URL}/api/graph/{job_id}")
                if graph_response.status_code == 200:
                    results["graph"] = graph_response.json()
                    print(f"✅ Retrieved data from graph endpoint")
                else:
                    print(f"❌ Failed to get data from graph endpoint: {graph_response.status_code}")
            except Exception as e:
                print(f"❌ Error accessing graph endpoint: {str(e)}")
    else:
        print(f"❌ Failed to get data from status endpoint: {status_response.status_code}")
        return None
    
    # Print a summary of results
    for key, data in results.items():
        print(f"\n--- {key.upper()} RESULTS ---")
        if key == "status":
            print(f"Status: {data.get('status')}")
            print(f"Progress: {data.get('progress', 'N/A')}%")
            if data.get('error'):
                print(f"Error: {data.get('error')}")
                print("🔍 This error helps diagnose what went wrong with the analysis")
            
        elif key == "graph":
            graph_data = data.get('dependency_graph', {})
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            print(f"Graph has {len(nodes)} nodes and {len(edges)} edges")
            
            # Print sample nodes if available
            if nodes:
                print("\nSample nodes:")
                for node in nodes[:3]:  # Show first 3 nodes
                    print(f"  - {node.get('id', 'unknown')}: {node.get('label', 'no label')}")
                    
    return results

def wait_for_completion(job_id, max_wait_time=60):
    """Wait for an analysis job to complete"""
    print(f"\n⏳ Waiting for job {job_id} to complete...")
    start_time = time.time()
    
    # Poll more frequently at first, then less frequently
    retry_count = 0
    
    while time.time() - start_time < max_wait_time:
        status = test_status(job_id)
        if status in ["completed", "failed"]:
            if status == "completed":
                print("✅ Job completed successfully")
                return True
            elif status == "failed":
                print("❌ Job failed")
                return False
        
        # Reduced waiting time for faster testing
        retry_count += 1
        wait_time = min(2 + (retry_count // 3), 5)  # Start at 2s, max 5s
        time.sleep(wait_time)
    
    print("❌ Timed out waiting for job to complete")
    return False

def get_analysis_details(job_id):
    """Get detailed analysis results including issues and summary"""
    print(f"\n📊 Getting detailed analysis results for job {job_id}...")
    
    # Create a custom endpoint to get all job data directly
    response = requests.get(f"{BASE_URL}/api/status/{job_id}")
    
    if response.status_code == 200:
        job_status = response.json()
        
        # Check if the job failed and show the error message
        if job_status.get('status') == 'failed':
            print("\n❌ Analysis job failed")
            print(f"Error: {job_status.get('error', 'Unknown error')}")
        
        # Try to get detailed job data using direct API calls 
        # This is just for testing - in production we would use proper endpoints
        try:
            detail_response = requests.get(f"{BASE_URL}/api/status/{job_id}?include_details=true")
            if detail_response.status_code == 200:
                job_data = detail_response.json()
                
                # Print summary
                print("\n📝 ANALYSIS SUMMARY:")
                print("-" * 30)
                if "summary" in job_data:
                    print(job_data["summary"])
                else:
                    print("No summary available")
                
                # Print issues
                if "issues" in job_data and job_data["issues"]:
                    print("\n⚠️ CODE ISSUES:")
                    print("-" * 30)
                    for idx, issue in enumerate(job_data["issues"], 1):
                        print(f"{idx}. {issue.get('file', 'Unknown file')} (line {issue.get('line', '?')})")
                        print(f"   Severity: {issue.get('severity', 'unknown')}")
                        print(f"   Message: {issue.get('message', 'No message')}")
                        print()
                else:
                    print("\nNo issues found or issues data not available")
                
                return job_data
        except Exception as e:
            print(f"Error getting detailed results: {str(e)}")
    
    print("❌ Could not retrieve detailed analysis results")
    return None

def run_all_tests():
    """Run all API tests"""
    print("🧪 STARTING API ENDPOINT TESTS 🧪")
    print("=" * 50)
    
    # Test basic endpoints
    health_ok = test_health()
    root_ok = test_root()
    
    if not health_ok or not root_ok:
        print("\n❌ Basic endpoint tests failed. Stopping tests.")
        return False
    
    # Test GitHub analysis flow
    print("\n" + "=" * 50)
    print("🔍 TESTING GITHUB ANALYSIS FLOW")
    print("=" * 50)
    github_job_id = test_github_analyze()
    if github_job_id:
        # Wait for the job to complete
        job_status = wait_for_completion(github_job_id)
        # Always get detailed job information regardless of status
        get_analysis_details(github_job_id)
        
        # Only test graph and report endpoints if the job was completed successfully
        if job_status is True:
            test_graph(github_job_id)
            test_report(github_job_id)
    
    # Test file upload flow
    print("\n" + "=" * 50)
    print("📤 TESTING FILE UPLOAD FLOW")
    print("=" * 50)
    upload_job_id = test_file_upload()
    if upload_job_id:
        # Wait for the job to complete
        job_status = wait_for_completion(upload_job_id)
        # Always get detailed job information regardless of status
        get_analysis_details(upload_job_id)
        
        # Only test graph endpoint if the job was completed successfully
        if job_status is True:
            test_graph(upload_job_id)
    
    print("\n" + "=" * 50)
    print("🏁 API ENDPOINT TESTS COMPLETED 🏁")
    
if __name__ == "__main__":
    run_all_tests()