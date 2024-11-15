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

    # Generate current state column based on the date
    current_time = datetime.now().strftime("%Y_%m_%d")
    state_column = f'state_for_{current_time}'  # Dynamically generated column name

    # Cleaned data with the dynamically generated column name
    cleaned_data = {
        'number': data.get("number"),
        'index': data.get('index', None),
        'Plaats': "Amsterdam",
        'Segment': 'Huur',
        'Project': 'AMST',
        'Bouwnummer': data.get('Woningtype', None),
        'Aantal kamers': clean_value(data.get('Aantal kamers', None)),
        'Prijs': clean_value(data.get('Huurprijs', None)),
        'Woonoppervlakte': clean_value(data.get('Woonoppervlakte', None)),
        'Buitenruimte type JA/NEE': data.get('Buitenruimte type JA/NEE'),
        'Oppervlakte buitenruimte': clean_value(data.get('Oppervlakte buitenruimte', None)),
        'Verdieping': data.get('Verdieping', 0),
        'Inclusief erfpacht prijs': clean_value(data.get('Inclusief erfpacht prijs', None)),
        'Meubileringkosten': clean_value(data.get('Meubileringkosten', None)),
        'Orientatie': data.get('Orientatie', None),
        'Servicekosten': clean_value(data.get('Servicekosten', None)),
        'Parkeren': data.get('Parkeren', None),
        'Website/bron': data.get('Website/bron', None),
        state_column: data.get('Status', None)  # Status mapped to dynamic column name
    }

    try:
        # Check if record with matching index exists
        check_exists_query = sql.SQL("""
            SELECT 1 FROM realty_data
            WHERE "number" = %s
        """)
        cursor.execute(check_exists_query, (cleaned_data['number'],))

        result = cursor.fetchone()
        if result:
            # Update query with dynamic column
            update_query = sql.SQL("""
                UPDATE realty_data SET
                "number" = %(number)s, "Plaats" = %(Plaats)s, "Segment" = %(Segment)s, "Project" = %(Project)s,
                "Bouwnummer" = %(Bouwnummer)s, "Aantal kamers" = %(Aantal kamers)s, "Prijs" = %(Prijs)s,
                "Woonoppervlakte" = %(Woonoppervlakte)s, "Buitenruimte type JA/NEE" = %(Buitenruimte type JA/NEE)s,
                "Oppervlakte buitenruimte" = %(Oppervlakte buitenruimte)s,
                "Inclusief erfpacht prijs" = %(Inclusief erfpacht prijs)s, "Meubileringkosten" = %(Meubileringkosten)s,
                "Orientatie" = %(Orientatie)s, "Servicekosten" = %(Servicekosten)s, "Parkeren" = %(Parkeren)s,
                "Website/bron" = %(Website/bron)s, {state_column} = %({state_column})s
                WHERE "index" = %(index)s AND "Verdieping" = %(Verdieping)s
            """).format(state_column=sql.SQL(state_column))

            cursor.execute(update_query, cleaned_data)
            print(f"Record updated successfully for index {cleaned_data['index']} and Verdieping {cleaned_data['Verdieping']}.")

        else:
            # Insert query with dynamic column
            insert_query = sql.SQL("""
                INSERT INTO realty_data (
                    "number", "index", "Plaats", "Segment", "Project", "Bouwnummer", "Aantal kamers", "Prijs", 
                    "Woonoppervlakte", "Buitenruimte type JA/NEE", "Oppervlakte buitenruimte", 
                    "Verdieping", "Inclusief erfpacht prijs", "Meubileringkosten", "Orientatie", 
                    "Servicekosten", "Parkeren", "Website/bron", {state_column}
                ) VALUES (
                    %(number)s, %(index)s, %(Plaats)s, %(Segment)s, %(Project)s, %(Bouwnummer)s, %(Aantal kamers)s, %(Prijs)s, 
                    %(Woonoppervlakte)s, %(Buitenruimte type JA/NEE)s, %(Oppervlakte buitenruimte)s, 
                    %(Verdieping)s, %(Inclusief erfpacht prijs)s, %(Meubileringkosten)s, %(Orientatie)s, 
                    %(Servicekosten)s, %(Parkeren)s, %(Website/bron)s, %({state_column})s
                )
            """).format(state_column=sql.SQL(state_column))

            cursor.execute(insert_query, cleaned_data)
            print(f"Record inserted successfully for index {cleaned_data['index']} and Verdieping {cleaned_data['Verdieping']}.")

        # Commit changes to the database
        connection.commit()

    except psycopg2.Error as e:
        print("Error inserting/updating data:", e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
