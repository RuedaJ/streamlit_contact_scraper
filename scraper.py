import requests
from bs4 import BeautifulSoup

def scrape_contacts(company_name):
    query = f'{company_name} site:linkedin.com/in ("CEO" OR "Investment Manager" OR "Real Estate Director")'
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    for link in soup.select("a"):
        href = link.get("href", "")
        if "linkedin.com/in" in href:
            results.append({
                "Company": company_name,
                "LinkedIn Profile": href
            })
    return results
