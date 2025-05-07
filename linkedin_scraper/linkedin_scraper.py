import requests
from bs4 import BeautifulSoup
import pandas as pd

# Example job site (replace with real or sample site if needed)
url = 'https://remoteok.com/remote-dev-jobs'
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

jobs = []

# Parse job cards
for job_card in soup.find_all('tr', class_='job'):
    title = job_card.find('h2')
    if title:
        title = title.text.strip()
        location = job_card.get('data-location', 'Remote')
        skills = [tag.text for tag in job_card.find_all('span', class_='tag')]
        jobs.append({'title': title, 'location': location, 'skills': skills})

# Save raw data
df = pd.DataFrame(jobs)
df.to_csv('raw_jobs.csv', index=False)
print("Scraping complete. Data saved.")
