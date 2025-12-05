import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

url = "https://www.vipusknik.kz/institutions/university"
response = requests.get(url)
response.raise_for_status()
html = response.text
soup = BeautifulSoup(html, "lxml")
links = soup.find_all("a", class_="text-blue-dark no-underline hover:underline")

# Создаем списки для хранения данных
names = []
uni_links = []

# Собираем данные
for link in links:
    href = link.get("href")
    name = link.get_text(separator=" ", strip=True)
    
    if href and name:  # Проверяем, что данные есть
        uni_links.append(href)
        names.append(name)
        print(f"Ссылка: {href}")
        print(f"Название: {name}\n")

# Создаем DataFrame
df = pd.DataFrame({
    'Название университета': names,
    'Ссылка': uni_links
})

# Записываем в Excel
output_file = 'universities.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"\nДанные успешно записаны в файл: {output_file}")
print(f"Всего университетов: {len(df)}")