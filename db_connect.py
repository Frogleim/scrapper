from datetime import datetime
import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5433"
}


def add_current_status():
    # Generate the column name based on today's date
    current_time = datetime.now().strftime("%Y_%m_%d")
    print(f"Adding column: {current_time}")

    try:
        # Establish connection to the database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Construct the ALTER TABLE query to add the column
        alter_table_query = sql.SQL("""
            ALTER TABLE realty_data
            ADD COLUMN IF NOT EXISTS {column_name} TEXT DEFAULT NULL;
        """).format(column_name=sql.Identifier(f'state_for_{current_time}'))

        # Execute the query
        cursor.execute(alter_table_query)

        # Commit the changes to the database
        connection.commit()

        print(f"Column {current_time} added successfully.")

    except Exception as e:
        print(f"Error adding column: {e}")
    finally:
        # Clean up: Close the cursor and the connection
        cursor.close()
        connection.close()


def clean_value(value):
    """
    Function to clean the values by removing unwanted suffixes such as 'm2' and 'p/mnd'.
    It also ensures that the value can be converted to appropriate types like float or int.
    """
    # Remove 'm2' and 'p/mnd' and any leading/trailing spaces
    if isinstance(value, str):
        value = value.replace('m2', '').replace('p/mnd', '').strip()

    # Try to convert the cleaned value to a float if it represents a number
    try:
        # Remove any extra spaces and convert to float
        return float(value.replace('€', '').replace(',', '.')) if value else None
    except ValueError:
        # If conversion fails, return the cleaned string
        return value

def insert_data(data):
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    add_current_status()

    # Get the current date for the state table
    current_time = datetime.now().strftime("%Y_%m_%d")
    state_table = f'state_for_{current_time}'  # Generate the state table name dynamically

    # Cleaned data with default for 'Buitenruimte type(JA/NEE)'
    cleaned_data = {'index': data.get('index', None), 'Plaats': "Amsterdam", 'Segment': 'Huur',
                    'Project': 'AMST', 'Bouwnummer': data.get('Woningtype', None),
                    'Aantal kamers': clean_value(data.get('Aantal kamers', None)),
                    'Prijs': clean_value(data.get('Huurprijs', None)),
                    'Woonoppervlakte': clean_value(data.get('Woonoppervlakte', None)),
                    'Buitenruimte type JA/NEE': data.get('Buitenruimte type JA/NEE'),
                    'Oppervlakte buitenruimte': clean_value(data.get('Oppervlakte buitenruimte', None)),
                    'Verdieping': clean_value(data.get('Verdieping', None)),
                    'Inclusief erfpacht prijs': clean_value(data.get('Inclusief erfpacht prijs', None)),
                    'Meubileringkosten': clean_value(data.get('Meubileringkosten', None)),
                    'Orientatie': data.get('Orientatie', None),
                    'Servicekosten': clean_value(data.get('Servicekosten', None)),
                    'Parkeren': data.get('Parkeren', None), 'Website/bron': data.get('Website/bron', None),
                    state_table: data.get('Status', None)}

    # Add the dynamically generated column value to the cleaned_data dictionary

    try:
        # SQL query to insert data into the realty_data table
        insert_query = sql.SQL("""
            INSERT INTO realty_data (
                "index", "Plaats", "Segment", "Project", "Bouwnummer", "Aantal kamers", "Prijs", 
                "Woonoppervlakte", "Buitenruimte type JA/NEE", "Oppervlakte buitenruimte", 
                "Verdieping", "Inclusief erfpacht prijs", "Meubileringkosten", "Orientatie", 
                "Servicekosten", "Parkeren", "Website/bron", {column_name}
            ) VALUES (
                %(index)s, %(Plaats)s, %(Segment)s, %(Project)s, %(Bouwnummer)s, %(Aantal kamers)s, %(Prijs)s, 
                %(Woonoppervlakte)s, %(Buitenruimte type JA/NEE)s, %(Oppervlakte buitenruimte)s, 
                %(Verdieping)s, %(Inclusief erfpacht prijs)s, %(Meubileringkosten)s, %(Orientatie)s, 
                %(Servicekosten)s, %(Parkeren)s, %(Website/bron)s, %({column_name})s
            )
        """).format(column_name=sql.SQL(state_table))

        # Execute the insert query with the cleaned data
        cursor.execute(insert_query, cleaned_data)
        connection.commit()

    except psycopg2.Error as e:
        print('Insert data error:', e)
        connection.rollback()

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()



def get_columns_sorted_by_creation(table_name):
    # Establish connection to the database
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    try:
        query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """
        cursor.execute(query, (table_name,))
        columns = cursor.fetchall()
        column_names = [column[0] for column in columns]
        print(f"Columns in table '{table_name}' sorted by creation order:")
        print(column_names)
        return column_names

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    today_column_name = datetime.now().strftime("%Y_%m_%d")
    data = {
        "Status": "Gereserveerd",
        "Huurprijs": "€ 1805 p/mnd",
        "Woningtype": "G1",
        "Woonoppervlakte": "50.60 m2",
        "Verdieping": "13",
        "Aantal kamers": "1",
        "Oppervlakte buitenruimte": "4.03 m2",
        "Balkonligging": "Zuid/oost",
        "Berging": "5.45 m2",
        "Energielabel": "A+++",
        "Buitenruimte type JA/NEE": "JA",
        "index": "AMST-G1"
    }
    table_name = "realty_data"
    insert_data(data)
