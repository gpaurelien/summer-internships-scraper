import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import typing as t
from src.models.job_offer import JobOffer
from src.utils.exceptions import ParsingError, ScrapingError
import logging
from src.repository.job_repository import JobRepository
from src.utils.markdown_export import export_to_markdown
from src.utils import LOCATIONS


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LinkedInScraper:
    """Entry point for LinkedIn job offers scraping"""

    def __init__(self, host: str, logger: logging.Logger = logger) -> None:
        self.host = host
        self.logger = logger

    def fetch_jobs(
            self,
            geo_id: str,
            keywords: str = "Summer 2025"
        ) -> t.Union[t.List[JobOffer] | None]:
        """
        Retrieves jobs, parses them, and returns a list containing offers.

        :param geo_id: The location ID used by LinkedIn (stored internally)
        :param keywords: Keywords needed for the research
        """

        if not isinstance(geo_id, str) or not isinstance(keywords, str):
            raise TypeError("'geo_id' and 'keywords' have to be str")

        self.logger.info(
            "Fetching jobs at %s with following pattern: '%s'"
            % (geo_id, keywords)
        )
        keywords = self._format_keywords(keywords)
        url = f"{self.host}/?keywords={keywords}&geoId={geo_id}"
        response = requests.get(url)
        if response.status_code != 200:
            raise ScrapingError("An error occured while requesting % s" % url)

        soup = BeautifulSoup(response.content, 'html.parser')
        cards = soup.find_all('div', class_='job-search-card')
        
        jobs = []
        filtered_count = 0
        total_count = len(cards)
        
        for card in cards:
            if not self._filter_cards(card):
                filtered_count += 1
                continue
            
            try:
                job = self._parse_job_card(card)
                jobs.append(job)
            except Exception as e:
                raise ParsingError("Error while parsing job card") from e
        
        self.logger.info(
            f"Found {len(jobs)} dev jobs out of {total_count} total jobs "
            f"(filtered out {filtered_count})"
        )
            
        return jobs
    
    def _format_keywords(self, keywords: str) -> str:
        return keywords.replace(" ", "%20")
    
    def _parse_job_card(self, card: Tag) -> JobOffer:
        """Extracts information from a job card"""

        title = card.find('h3', class_='base-search-card__title').text.strip()
        name = card.find('h4', class_='base-search-card__subtitle').text.strip()
        location = card.find('span', class_='job-search-card__location').text.strip()
        link = card.find('a', class_='base-card__full-link')
        url = link.get('href') if link else None
        datetime_elements = card.find('time')
        posted_date = datetime_elements.get('datetime') if datetime_elements else None
        
        return JobOffer(
            title=title,
            company_name=name,
            location=location,
            url=url,
            posted_date=posted_date,
            description=None
        )
    
    def _filter_cards(self, card: Tag) -> bool:
        """
        Filter job cards based on development-related keywords in the title.
        Must contain 'intern' and at least one dev-related keyword.
        Returns True if the card should be kept, False otherwise.
        """

        dev_keywords = {
            'software', 'developer', 'engineer', 'backend', 'frontend',
            'fullstack', 'full-stack', 'web', 'cloud', 'devops',
            'development', 'engineering', 'mobile'
        }
        
        title = card.find('h3', class_='base-search-card__title')
        if not title:
            return False
        
        title_text = title.text.strip().lower()
        if 'intern' not in title_text:
            return False

        return any(keyword in title_text for keyword in dev_keywords)
    
    
def main():
    scraper = LinkedInScraper("https://www.linkedin.com/jobs/search")
    repo = JobRepository()
    
    for location, geo_id in LOCATIONS.items():
        logger.info(f"Fetching jobs for {location}")
        jobs = scraper.fetch_jobs(geo_id=geo_id, keywords="Summer 2025")
        new_jobs, total_jobs = repo.add_jobs(jobs)
        logger.info(f"Added {new_jobs} new jobs. Total jobs in storage: {total_jobs}")
    
    all_jobs = repo.get_all_jobs()
    export_to_markdown(all_jobs)
    logger.info(f"Generated markdown file with {len(all_jobs)} jobs")

if __name__ == "__main__":
    main()