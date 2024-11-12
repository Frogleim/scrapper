import requests
from bs4 import BeautifulSoup as BS
import json
import pandas as pd
import re
from db_connect import insert_data
from save_excel import run
# Initialize the listings_data list to store the results
listings_data = []

url = 'https://thepulse-living.nl/woningvinder/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
    # Customize as needed
    'Accept': 'application/json'  # Specify expected response format if needed
}

r = requests.get(url, headers=headers)
print(r.status_code)  # Check if the request was successful
soup = BS(r.content, 'html.parser')
rows = soup.find_all('div', class_='row')
woningurls = [row.get("data-woningurl") for row in rows if row.get("data-woningurl")]
i = 0
for woningurl in woningurls:
    if 'woning' in woningurl:  # Check if the URL is valid
        i += 1
        try:
            appartment_request = requests.get(woningurl, headers=headers)
            appartment_soup = BS(appartment_request.text, 'html.parser')
            table = appartment_soup.find('table', class_='specificatietabel')

            if table:
                data_dict = {}
                for cell in table.find_all('td'):
                    key = cell.find('b').text.strip() if cell.find('b') else ''
                    value = cell.text.replace(key, '').strip()
                    if key:
                        data_dict[key] = value

                # Add "Buitenruimte type(JA/NEE)" based on the presence of "Oppervlakte buitenruimte"
                data_dict["Buitenruimte type JA/NEE"] = "JA" if "Oppervlakte buitenruimte" in data_dict else "NEE"
                data_dict['index'] = f"AMST-{data_dict['Woningtype']}"
                data_dict['segment'] = 'Huur'
                data_dict['Website/bron'] = 'https://thepulse-living.nl/woning'
                insert_data(data_dict)
                run()

                print(json.dumps(data_dict, ensure_ascii=False, indent=4))
            else:
                print(f"Table not found for {woningurl}")

        except Exception as e:
            print(f"Error processing {woningurl}: {e}")

# Save the data to a JSON file
with open('listings_data.json', 'w', encoding='utf-8') as f:
    json.dump(listings_data, f, ensure_ascii=False, indent=4)
