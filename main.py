import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.scrapers.linkedin_scraper import LinkedInScraper

def main():
    scraper = LinkedInScraper()
    jobs = scraper.fetch_jobs()
    
    # Afficher les résultats
    for job in jobs:
        print(f"\n{'='*50}")
        print(f"Titre: {job.title}")
        print(f"Entreprise: {job.company_name}")
        print(f"Localisation: {job.location}")
        print(f"Date de publication: {job.posted_date}")
        print(f"URL: {job.url}")
        
        # Optionnel : récupérer la description complète
        if job.url:
            description = scraper.get_job_description(job.url)
            print(f"\nDescription: {description[:200]}...")

if __name__ == "__main__":
    main()
