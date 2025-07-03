import requests
from bs4 import BeautifulSoup
import streamlit as st

ROLE_KEYWORDS = [
    "Real Estate", "Real Estate Development", "Development Director",
    "Real Estate Director", "Asset Manager", "Asset Management",
    "Real Estate Investment", "Real Estate Investment Manager",
    "Director Tecnico", "Head of Real Estate", "Project Manager",
    "Director de Inversiones", "Portfolio Manager", "Director", "Manager", "Partner", "Head"
]

SERPAPI_KEY = st.secrets["api_keys"]["serpapi"]

def role_matches(text):
    for keyword in ROLE_KEYWORDS:
        if keyword.lower() in text.lower():
            return True
    return False

def enrich_email_placeholder(name, company):
    guessed_email = f"{name.lower().replace(' ', '.')}@{company.lower().replace(' ', '').replace('.', '')}.com"
    return guessed_email, "Yes (guessed)"

def scrape_contacts(company_name, location_hint=""):
    contacts = []
    headers = {"User-Agent": "Mozilla/5.0"}

    # Enhance query with company and location
    base_query = f'site:linkedin.com/in "{company_name}" {location_hint} (CEO OR Investment OR Real Estate OR Director OR Manager OR Partner OR Head)'

    # Use SerpAPI if available
    if SERPAPI_KEY:
        serpapi_url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": base_query,
            "api_key": SERPAPI_KEY,
            "num": 20
        }
        response = requests.get(serpapi_url, params=params)
        if response.status_code == 200:
            data = response.json()
            for result in data.get("organic_results", []):
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                combined = title + " " + snippet
                if "linkedin.com/in" in link and role_matches(combined):
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

    # Fallback to direct Google scraping
    search_url = f"https://www.google.com/search?q={requests.utils.quote(base_query)}"
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    for link in soup.select("a"):
        href = link.get("href", "")
        text = link.text.strip()
        if "linkedin.com/in" in href and "webcache" not in href and role_matches(text):
            clean_url = href.split("/url?q=")[-1].split("&")[0]
            name = text.split("|")[0].strip()
            email, source = enrich_email_placeholder(name, company_name)
            contacts.append({
                "Company": company_name,
                "Name & Title": text,
                "LinkedIn Profile": clean_url,
                "Email": email,
                "Email Enriched": source
            })

    return contacts
