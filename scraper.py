import requests
from bs4 import BeautifulSoup
import os

ROLE_KEYWORDS = [
    "Real Estate", "Real Estate Development", "Development Director",
    "Real Estate Director", "Asset Manager", "Asset Management",
    "Real Estate Investment", "Real Estate Investment Manager",
    "Director Tecnico", "Head of Real Estate", "Project Manager",
    "Director de Inversiones", "Portfolio Manager"
]

SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # Set this in your environment

def role_matches(text):
    for keyword in ROLE_KEYWORDS:
        if keyword.lower() in text.lower():
            return True
    return False

def enrich_email_placeholder(name, company):
    guessed_email = f"{name.lower().replace(' ', '.')}@{company.lower().replace(' ', '')}.com"
    return guessed_email, "Yes (guessed)"

def scrape_contacts(company_name):
    contacts = []

    # Step 1: Try SerpAPI
    if SERPAPI_KEY:
        serpapi_url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": f'site:linkedin.com/in "{company_name}"',
            "api_key": SERPAPI_KEY,
            "num": 10
        }
        response = requests.get(serpapi_url, params=params)
        if response.status_code == 200:
            data = response.json()
            for result in data.get("organic_results", []):
                title = result.get("title", "")
                link = result.get("link", "")
                if "linkedin.com/in" in link and role_matches(title):
                    name = title.split("|")[0].strip()
                    email, source = enrich_email_placeholder(name, company_name)
                    contacts.append({
                        "Company": company_name,
                        "Name & Title": title,
                        "LinkedIn Profile": link,
                        "Email": email,
                        "Email Enriched": source
                    })
            if contacts:
                return contacts

    # Step 2: Fallback to basic Google scraping
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f'site:linkedin.com/in "{company_name}"'
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    for link in soup.select("a"):
        href = link.get("href", "")
        text = link.text.strip()
        if "linkedin.com/in" in href and "webcache" not in href and role_matches(text):
            name = text.split("|")[0].strip()
            email, source = enrich_email_placeholder(name, company_name)
            contacts.append({
                "Company": company_name,
                "Name & Title": text,
                "LinkedIn Profile": href,
                "Email": email,
                "Email Enriched": source
            })

    return contacts
