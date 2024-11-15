import requests
from bs4 import BeautifulSoup as BS
import json
import re
from db_connect import insert_data
from save_excel import run

# Initialize the listings_data list to store the results
listings_data = []

url = 'https://thepulse-living.nl/woningvinder/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
    'Accept': 'application/json'
}

r = requests.get(url, headers=headers)
print(r.status_code)  # Check if the request was successful
soup = BS(r.content, 'html.parser')
rows = soup.find_all('div', class_='row')
woningurls = [row.get("data-woningurl") for row in rows if row.get("data-woningurl")]
i = 0
print(len(woningurls))
for woningurl in woningurls:
    if 'woning' in woningurl:  # Check if the URL is valid
        i += 1
        print(woningurl)

        # Check if regex matches before accessing group(1)
        match = re.search(r"-([0-9]+)/?$", woningurl)
        if match:
            number = match.group(1)
            print(number)
        else:
            print(f"No number found in URL: {woningurl}")
            continue  # Skip this woningurl if no match is found

        print(f'Apartment #{i}')

        # Reset data_dict for each apartment
        data_dict = {}

        try:
            appartment_request = requests.get(woningurl, headers=headers)
            appartment_soup = BS(appartment_request.text, 'html.parser')
            table = appartment_soup.find('table', class_='specificatietabel')

            if table:
                for cell in table.find_all('td'):
                    key = cell.find('b').text.strip() if cell.find('b') else ''
                    value = cell.text.replace(key, '').strip()

                    if key:
                        data_dict[key] = value

                # Add custom fields
                data_dict['number'] = number
                data_dict['index'] = f"AMST-{data_dict.get('Woningtype', '')}"
                data_dict["Buitenruimte type JA/NEE"] = "JA" if "Oppervlakte buitenruimte" in data_dict else "NEE"

                data_dict['segment'] = 'Huur'
                data_dict['Website/bron'] = 'https://thepulse-living.nl/woning'

                # Set 'Verdieping' with a default of '0' if missing
                data_dict['Verdieping'] = data_dict.get('Verdieping', '0')

                # Append to listings_data
                listings_data.append(data_dict)

                # Insert data into the database and run other processes
                insert_data(data_dict)
                run()
            else:
                print(f"Table not found for {woningurl}")

        except Exception as e:
            print(f"Error processing {woningurl}: {e}")

# Save the data to a JSON file
with open('listings_data.json', 'w', encoding='utf-8') as f:
    json.dump(listings_data, f, ensure_ascii=False, indent=4)
