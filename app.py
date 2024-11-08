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

for woningurl in woningurls:
    if 'woning' in woningurl:
        appartment_request = requests.get(woningurl, headers=headers)
        pattern = r'\{.*?\}'
        matches = re.findall(pattern, appartment_request.text)
        appartment_soup = BS(appartment_request.text, 'html.parser')
        table = appartment_soup.find('table', class_='specificatietabel')

        variables = {}

        # Iterate through the rows of the table
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            for cell in cells:
                # Get the title from the <b> tag
                try:
                    title = cell.find('b').get_text(strip=True).replace(' ', '_').lower()
                except AttributeError:
                    title = 'no title'
                    # Get the text after the first <br> tag
                br_tag = cell.find('br')
                value = br_tag.next_sibling.strip() if br_tag and br_tag.next_sibling else ""

                # Store the title and value in the dictionary
                variables[title] = value

        # Print the extracted data
        clean_data = []
        for title, value in variables.items():
            print('Saving values')
            clean_data.append(value)
        segment = clean_data[0]
        price = clean_data[1]
        cleaned_price = int(re.search(r"\d+", price).group())
        building_number = clean_data[2]
        living_area = clean_data[3]
        cleaned_living_area = living_area.replace('m2', '')
        floor = clean_data[4]
        rooms_number = clean_data[5]
        surface_outdoor = clean_data[6].replace('m2', '')
        current_time = datetime.now().strftime("%Y_%m_%d")

        data_dict = {
            "location": "Amsterdam",
            "segment": f"Huur",
            "project": "PLS",
            "building_number": f"{building_number}",
            "rooms_numbers": rooms_number,
            "price": cleaned_price,
            "living_area": cleaned_living_area,
            "outdoor_space_type": "Balcony",
            "surface_area_of_outdoor_space": surface_outdoor,
            "floor": floor,
            "leasehold_price": None,  # NULL value
            "furnishing_cost": None,
            "orientation": None,
            "service_cost": None,
            "parking": None,
            "website": url,
            f"state_for_{current_time}": segment


        }
        insert_data(data_dict)
        listings_data.append(data_dict)


current_time = datetime.now().strftime("%Y_%m_%d")
df = pd.DataFrame(listings_data)

# Save the DataFrame to an Excel file
output_file = f"realty_data_{current_time}.xlsx"
df.to_excel(output_file, index=False)
print(f"Data saved to {output_file}")