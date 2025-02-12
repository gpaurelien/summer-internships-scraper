import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List
from ..models.job_offer import JobOffer
from ..utils.exceptions import ParsingError, ScrapingError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, host: str, logger: logging.Logger = logger) -> None:
        self.host = host
        self.logger = logger

    def fetch_jobs(self, geo_id: str, keywords: str = "Summer 2025") -> str:
        keywords = self._format_keywords(keywords)
        url = f"{self.host}/?keywords={keywords}&geoId={geo_id}"
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')
        job_cards = soup.find_all('div', class_='job-search-card')
        
        jobs = []
        for card in job_cards:
            try:
                print(card)
                job = self._parse_job_card(card)
                jobs.append(job)
            except Exception as e:
                raise ParsingError("Error while parsing job card") from e
                
        return jobs
    
    def _format_keywords(self, keywords: str) -> str:
        return keywords.replace(" ", "%20")
    
    def _parse_job_card(self, card) -> JobOffer:
        """Extracts information from a job card"""

        title = card.find('h3', class_='base-search-card__title').text.strip()
        company_name = card.find('h4', class_='base-search-card__subtitle').text.strip()
        location = card.find('span', class_='job-search-card__location').text.strip()
        job_link = card.find('a', class_='base-card__full-link')
        url = job_link.get('href') if job_link else None

        date_elem = card.find('time')
        posted_date = date_elem.get('datetime') if date_elem else None
        
        return JobOffer(
            title=title,
            company_name=company_name,
            location=location,
            url=url,
            posted_date=posted_date,
            description=None
        )
    
    def get_job_description(self, job_url: str) -> str:
        """Récupère la description détaillée d'une offre"""
        response = requests.get(job_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        description_div = soup.find('div', class_='show-more-less-html__markup')
        return description_div.text.strip() if description_div else ""
    
scraper = LinkedInScraper("https://www.linkedin.com/jobs/search/?")
scraper.fetch_jobs(geo_id="100364837", keywords="Summer 2025")