"""
Advanced API tests for CQ Lite with asyncio and parallel testing
"""

import aiohttp
import asyncio
import json
import time
import os
from pathlib import Path
import sys
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

# Define the API base URL
BASE_URL = "http://localhost:8000"

class ApiTester:
    def __init__(self, base_url: str = BASE_URL, verbose: bool = True):
        self.base_url = base_url
        self.verbose = verbose
        self.session = None
        self.test_results = {}
    
    async def setup(self):
        """Setup async HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def teardown(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
    
    def log(self, message: str):
        """Log messages if verbose mode is enabled"""
        if self.verbose:
            print(message)
    
    async def test_health(self) -> bool:
        """Test the health check endpoint"""
        self.log("\n📋 Testing health check endpoint...")
        
        async with self.session.get(f"{self.base_url}/api/health") as response:
            status = response.status
            if status == 200:
                data = await response.json()
                self.log("✅ Health check endpoint is responding")
                self.log(f"Status: {data['status']}")
                self.log("Services status:")
                for service, svc_status in data['services'].items():
                    status_icon = "✅" if svc_status else "❌"
                    self.log(f"  - {service}: {status_icon}")
                self.test_results['health'] = True
                return True
            else:
                self.log(f"❌ Health check failed with status code {status}")
                text = await response.text()
                self.log(text)
                self.test_results['health'] = False
                return False
    
    async def test_github_analyze(self, repo_url: str) -> Optional[str]:
        """Test the GitHub repository analysis endpoint"""
        self.log("\n📋 Testing GitHub repository analysis endpoint...")
        
        payload = {
            "repository_url": repo_url,
            "branch": "master",
            "include_dependencies": True,
            "include_docker": True
        }
        
        async with self.session.post(
            f"{self.base_url}/api/github/analyze", 
            json=payload
        ) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                self.log("✅ GitHub analysis endpoint is responding")
                self.log(f"Job ID: {data['job_id']}")
                self.log(f"Status: {data['status']}")
                self.test_results['github_analyze'] = True
                return data['job_id']
            else:
                self.log(f"❌ GitHub analysis endpoint failed with status code {status}")
                text = await response.text()
                self.log(text)
                self.test_results['github_analyze'] = False
                return None
    
    async def test_status(self, job_id: str) -> Optional[str]:
        """Test the analysis status endpoint"""
        self.log(f"\n📋 Testing analysis status endpoint for job {job_id}...")
        
        async with self.session.get(f"{self.base_url}/api/status/{job_id}") as response:
            status = response.status
            if status == 200:
                data = await response.json()
                self.log("✅ Status endpoint is responding")
                self.log(f"Status: {data['status']}")
                progress = data.get('progress', 'N/A')
                self.log(f"Progress: {progress}%")
                self.test_results['status'] = True
                return data['status']
            else:
                self.log(f"❌ Status endpoint failed with status code {status}")
                text = await response.text()
                self.log(text)
                self.test_results['status'] = False
                return None
    
    async def test_graph(self, job_id: str) -> bool:
        """Test the dependency graph endpoint"""
        self.log(f"\n📋 Testing dependency graph endpoint for job {job_id}...")
        
        async with self.session.get(f"{self.base_url}/api/graph/{job_id}") as response:
            status = response.status
            if status == 200:
                data = await response.json()
                self.log("✅ Graph endpoint is responding")
                node_count = len(data.get('graph', {}).get('nodes', []))
                edge_count = len(data.get('graph', {}).get('edges', []))
                self.log(f"Number of nodes: {node_count}")
                self.log(f"Number of edges: {edge_count}")
                self.test_results['graph'] = True
                return True
            else:
                self.log(f"❌ Graph endpoint failed with status code {status}")
                text = await response.text()
                self.log(text)
                self.test_results['graph'] = False
                return False
    
    async def test_report(self, job_id: str) -> bool:
        """Test the report generation endpoint"""
        self.log(f"\n📋 Testing report generation endpoint for job {job_id}...")
        
        payload = {
            "job_id": job_id,
            "format": "html"
        }
        
        async with self.session.post(
            f"{self.base_url}/api/report/generate", 
            json=payload
        ) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                self.log("✅ Report endpoint is responding")
                self.log(f"Report URL: {data['report_url']}")
                self.test_results['report'] = True
                return True
            else:
                self.log(f"❌ Report endpoint failed with status code {status}")
                text = await response.text()
                self.log(text)
                self.test_results['report'] = False
                return False
    
    async def test_file_upload(self) -> Optional[str]:
        """Test the file upload endpoint"""
        self.log("\n📋 Testing file upload endpoint...")
        
        # Create a simple test file
        test_file_path = Path("test_upload.py")
        with open(test_file_path, "w") as f:
            f.write('print("Hello from test file")\n\nclass TestClass:\n    def test_method(self):\n        return "Test"')
        
        try:
            data = aiohttp.FormData()
            data.add_field('file', 
                          open(test_file_path, 'rb'),
                          filename='test_upload.py',
                          content_type='application/octet-stream')
            
            async with self.session.post(
                f"{self.base_url}/api/upload/file", 
                data=data
            ) as response:
                status = response.status
                if status == 200:
                    resp_data = await response.json()
                    self.log("✅ File upload endpoint is responding")
                    self.log(f"Upload ID: {resp_data['upload_id']}")
                    file_id = resp_data['upload_id']
                    self.test_results['file_upload'] = True
                    
                    # Test file analysis
                    return await self.test_file_analysis(file_id)
                else:
                    self.log(f"❌ File upload endpoint failed with status code {status}")
                    text = await response.text()
                    self.log(text)
                    self.test_results['file_upload'] = False
                    return None
        finally:
            # Clean up test file
            if test_file_path.exists():
                test_file_path.unlink()
    
    async def test_file_analysis(self, file_id: str) -> Optional[str]:
        """Test file analysis endpoint"""
        self.log("\n📋 Testing file analysis endpoint...")
        
        payload = {
            "file_id": file_id,
            "include_dependencies": True
        }
        
        async with self.session.post(
            f"{self.base_url}/api/upload/analyze", 
            json=payload
        ) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                self.log("✅ File analysis endpoint is responding")
                self.log(f"Job ID: {data['job_id']}")
                self.test_results['file_analysis'] = True
                return data['job_id']
            else:
                self.log(f"❌ File analysis endpoint failed with status code {status}")
                text = await response.text()
                self.log(text)
                self.test_results['file_analysis'] = False
                return None
    
    async def wait_for_completion(self, job_id: str, max_wait_time: int = 60) -> bool:
        """Wait for an analysis job to complete"""
        self.log(f"\n⏳ Waiting for job {job_id} to complete...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = await self.test_status(job_id)
            if status in ["completed", "failed"]:
                return status == "completed"
            await asyncio.sleep(5)
        
        self.log("❌ Timed out waiting for job to complete")
        return False
    
    async def run_tests(self, github_repo: str = "https://github.com/Ankur2606/CQ-Lite"):
        """Run all API tests"""
        self.log("🧪 STARTING API ENDPOINT TESTS 🧪")
        self.log("=" * 50)
        start_time = time.time()
        
        # Setup session
        await self.setup()
        
        try:
            # Test basic endpoints
            health_ok = await self.test_health()
            
            if not health_ok:
                self.log("\n❌ Health check failed. Stopping tests.")
                return
            
            # Start tests in parallel
            tasks = []
            
            # GitHub analysis flow
            tasks.append(self.test_github_workflow(github_repo))
            
            # File upload flow
            tasks.append(self.test_file_workflow())
            
            # Wait for all test workflows to complete
            await asyncio.gather(*tasks)
            
            # Print summary
            self.log("\n" + "=" * 50)
            self.log("🏁 API ENDPOINT TESTS COMPLETED 🏁")
            duration = time.time() - start_time
            self.log(f"Tests completed in {duration:.2f} seconds")
            
            # Print results summary
            self.log("\n📊 TEST RESULTS SUMMARY:")
            for test_name, result in self.test_results.items():
                status_icon = "✅" if result else "❌"
                self.log(f"{status_icon} {test_name}")
        
        finally:
            # Cleanup
            await self.teardown()
    
    async def test_github_workflow(self, github_repo: str):
        """Run the complete GitHub analysis workflow"""
        github_job_id = await self.test_github_analyze(github_repo)
        if github_job_id:
            # Wait for the job to complete
            if await self.wait_for_completion(github_job_id):
                # Test dependent endpoints once analysis is complete
                await self.test_graph(github_job_id)
                await self.test_report(github_job_id)
    
    async def test_file_workflow(self):
        """Run the complete file upload workflow"""
        upload_job_id = await self.test_file_upload()
        if upload_job_id:
            await self.wait_for_completion(upload_job_id)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test the CQ Lite API")
    parser.add_argument("--url", default=BASE_URL, help="Base URL of the API server")
    parser.add_argument("--repo", default="https://github.com/Ankur2606/CQ-Lite", 
                       help="GitHub repository URL to test")
    parser.add_argument("--quiet", action="store_true", help="Run in quiet mode")
    return parser.parse_args()

async def main():
    """Main entry point"""
    args = parse_args()
    tester = ApiTester(base_url=args.url, verbose=not args.quiet)
    await tester.run_tests(github_repo=args.repo)

if __name__ == "__main__":
    asyncio.run(main())