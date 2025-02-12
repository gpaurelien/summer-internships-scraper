from dataclasses import dataclass


@dataclass
class Company:
    name: str
    industry: str
    size: str
    website: str
    linkedin_url: str 