import json
import logging
import typing as t
from datetime import datetime
from pathlib import Path

from src.models.job_offer import JobOffer

logger = logging.getLogger(__name__)

class JobRepository:
    def __init__(
        self,
        storage_path: str = "data/jobs.json",
        logger: logging.Logger = logger
    ) -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_exists()
        self.logger = logger
        
    def _ensure_storage_exists(self):
        """Create storage file if it doesn't exist"""
        if not self.storage_path.exists():
            self.storage_path.write_text('{}')
            
    def _load_jobs(self) -> dict:
        """Load all jobs from storage"""
        try:
            return json.loads(self.storage_path.read_text())
        except json.JSONDecodeError:
            self.logger.error("Corrupted storage file")
            return {}
            
    def _save_jobs(self, jobs: dict):
        """Save jobs to storage"""
        self.storage_path.write_text(json.dumps(jobs, indent=2))
        
    def add_jobs(self, jobs: t.List[JobOffer]) -> t.Tuple[int, int]:
        """Add new jobs to storage, avoiding duplicates based on their hashes."""

        storage = self._load_jobs()
        
        new_jobs = 0
        for job in jobs:
            job_hash = job.get_hash()
            if job_hash not in storage:
                storage[job_hash] = job.to()
                storage[job_hash]['first_seen'] = datetime.now().isoformat()
                new_jobs += 1
                
        self._save_jobs(storage)
        
        return new_jobs, len(storage)
    
    def get_all_jobs(self) -> t.List[dict]:
        """Retrieve all stored jobs"""
        return list(self._load_jobs().values())
    
    def get_recent_jobs(self, days: int = 7) -> t.List[dict]:
        """Get jobs seen in the last X days"""
        storage = self._load_jobs()
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        recent_jobs = []
        for job in storage.values():
            first_seen = datetime.fromisoformat(job['first_seen']).timestamp()
            if first_seen >= cutoff:
                recent_jobs.append(job)
                
        return recent_jobs 
