from dataclasses import dataclass
from datetime import datetime


@dataclass
class JobOffer:
    title: str
    company_name: str
    location: str
    posted_date: datetime
    description: str
    url: str 