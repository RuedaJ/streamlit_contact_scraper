import streamlit as st
import pandas as pd
from scraper import scrape_contacts

st.title("🔍 Contact Scraper – Real Estate & Investment Leads")

st.markdown("Upload a company list CSV (or use default).")

uploaded_file = st.file_uploader("Upload .csv with column 'Company'", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("input/default_companies.csv")
    st.info("Using default company list.")

st.write("Companies to scrape:", df)

if st.button("Start Scraping"):
    all_results = []
    for company in df["Company"]:
        st.write(f"🔎 Searching: {company}")
        results = scrape_contacts(company)
        all_results.extend(results)

    if all_results:
        results_df = pd.DataFrame(all_results)
        st.success("✅ Scraping completed.")
        st.dataframe(results_df)
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "contacts.csv", "text/csv")
    else:
        st.warning("No contacts found.")
