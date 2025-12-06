import requests
from bs4 import BeautifulSoup
import pandas as pd

file_path = 'university_links.xlsx'
urls_df = pd.read_excel(file_path, usecols=[0])
urls = urls_df.iloc[:, 0].dropna().tolist()

rows = []

for url in urls:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        
        specialities = []
        for a in soup.find_all("a", class_="block text-black text-grey-darkest"):
            text = a.get_text(separator=" ", strip=False)
            if text:
                specialities.append(text)   

        combined_specialities = "\n".join(specialities)

        paragraphs = []
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text:
                paragraphs.append(text)
        
        combined_text = "\n\n".join(paragraphs)
        
        websites = []
        for a in soup.find_all("a", class_="block px-8 py-1 text-sm text-blue-dark text-center font-bold bg-white opacity-90"):
            text = a.get_text(separator=" ", strip=True)
            if text:
                websites.append(text)

        combined_websites = "\n".join(websites)

        contacts = []
        for a in soup.find_all("a", class_="text-green-light lg:text-lg lg:text-white lg:no-underline"):
            text = a.get_text(separator=" ", strip=True)
            if text:
                contacts.append(text)

        combined_contacts = "\n".join(contacts)

        addresses = []
        for div in soup.find_all("div", class_="lg:text-white lg:text-xl"):
            text = div.get_text(separator=" ", strip=True)
            if text:
                addresses.append(text)

        combined_address = "\n".join(addresses)

        rows.append({
            "page_url": url,
            "paragraph_text": combined_text,
            "specialities": combined_specialities,
            "websites": combined_websites,
            "contacts": combined_contacts,
            "address": combined_address
        })
        
        print(f"Processed: {url}")
        
    except Exception as e:
        print(f"Error processing {url}: {e}")
        rows.append({
            "page_url": url,
            "paragraph_text": f"ERROR: {str(e)}"
        })

out_df = pd.DataFrame(rows, columns=["page_url", "paragraph_text", "specialities", "websites", "contacts", "address"])
out_df.to_excel("university_data.xlsx", index=False)
print(f"\nSaved {len(out_df)} rows to university_data.xlsx")