import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
url = "https://www.vipusknik.kz/institutions/university/universitet-imeni-suleymana-demirelya"
response = requests.get(url)
response.raise_for_status()
html = response.text
soup = BeautifulSoup(html, "lxml")
texts = soup.find_all("p")
for p in texts:
    text = p.get_text(separator=" ", strip=True)
    if text:
        print(text)