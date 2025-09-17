"""
Shared job store service for analysis jobs.
This ensures all routers access the same job store.
"""

from typing import Dict, Any

class JobStore:
    """
    Singleton class to store analysis jobs in memory.
    In a production environment, this should be replaced with a database.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobStore, cls).__new__(cls)
            # Initialize the jobs dictionary
            cls._instance.jobs = {}
        return cls._instance
    
    def add_job(self, job_id: str, job_data: Dict[str, Any]) -> None:
        """Add a new job to the store"""
        self.jobs[job_id] = job_data
        
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get a job from the store"""
        return self.jobs.get(job_id)
        
    def update_job(self, job_id: str, job_data: Dict[str, Any]) -> None:
        """Update an existing job in the store"""
        if job_id in self.jobs:
            self.jobs[job_id].update(job_data)
            
    def delete_job(self, job_id: str) -> None:
        """Delete a job from the store"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            
    def list_jobs(self) -> Dict[str, Dict[str, Any]]:
        """List all jobs in the store"""
        return self.jobs


# Singleton instance for global access
_job_store = JobStore()

def get_job_store() -> JobStore:
    """Get the singleton job store instance"""
    return _job_store