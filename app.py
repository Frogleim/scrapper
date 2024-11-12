import requests
from bs4 import BeautifulSoup as BS
import re
import json
import time
import pandas as pd
from db_connect import insert_data, get_columns_sorted_by_creation
import re
from datetime import datetime


listings_data = []

url = 'https://thepulse-living.nl/woningvinder/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',  # Customize as needed
    'Accept': 'application/json'  # Specify expected response format if needed
}
data = []

r = requests.get(url, headers=headers)
print(r.status_code)
# columns = get_columns_sorted_by_creation('realty_data')
soup = BS(r.content, 'html.parser')
rows = soup.find_all('div', class_='row')
woningurls = [row.get("data-woningurl") for row in rows if row.get("data-woningurl")]
i = 0
for woningurl in woningurls:
    if 'woning' in woningurl:
        i+=1
        appartment_request = requests.get(woningurl, headers=headers)
        pattern = r'\{.*?\}'
        matches = re.findall(pattern, appartment_request.text)
        appartment_soup = BS(appartment_request.text, 'html.parser')
        table = appartment_soup.find('table', class_='specificatietabel')

        variables = {}
        data_dict = {}
        # Iterate through the rows of the table
        try:
            for cell in table.find_all('td'):
                key = cell.find('b').text.strip()  # Extract and clean the key
                value = cell.text.replace(key, '').strip()  # Extract and clean the value
                data_dict[key] = value  # Store in the dictionary
            json_data = json.dumps(data_dict, ensure_ascii=False, indent=4)

        # Output the JSON data
            print(json_data)
        except Exception as e:
            print('Not found')
        # Print the extracted data
        # clean_data = []
        # for title, value in variables.items():
        #     print('Saving values')
        #     clean_data.append(value)
        # segment = clean_data[0]
        # price = clean_data[1]
        # cleaned_price = int(re.search(r"\d+", price).group())
        # building_number = clean_data[2]
        # living_area = clean_data[3]
        # cleaned_living_area = living_area.replace('m2', '')
        # floor = clean_data[4]
        # rooms_number = clean_data[5]
        # surface_outdoor = clean_data[6].replace('m2', '')
        # current_time = datetime.now().strftime("%Y_%m_%d")
        # outdoor_space_type = 'Yes' if type(surface_outdoor) == float else 'No'
        # data_dict = {
        #     "index": f'AMST-{i}',
        #     "location": "Amsterdam",
        #     "segment": f"Huur",
        #     "project": "AMST",
        #     "building_number": f"{building_number}",
        #     "rooms_numbers": rooms_number,
        #     "price": cleaned_price,
        #     "living_area": cleaned_living_area,
        #     "outdoor_space_type": outdoor_space_type,
        #     "surface_area_of_outdoor_space": surface_outdoor if outdoor_space_type == 'Yes' else None,
        #     "floor": floor,
        #     "leasehold_price": None,  # NULL value
        #     "furnishing_cost": None,
        #     "orientation": None,
        #     "service_cost": None,
        #     "parking": None,
        #     "website": url,
        #     f"state_for_{current_time}": segment
        #
        #
        # }
        # insert_data(data_dict)
        # listings_data.append(data_dict)


current_time = datetime.now().strftime("%Y_%m_%d")
df = pd.DataFrame(listings_data)

# Save the DataFrame to an Excel file
output_file = f"realty_data_{current_time}.xlsx"
df.to_excel(output_file, index=False)
print(f"Data saved to {output_file}")