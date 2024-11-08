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


def insert_data(data):
    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()
    add_current_status()
    current_time = datetime.now().strftime("%Y_%m_%d")
    state_table = f'state_for_{current_time}'
    try:

        # Create the insert query with dynamic column name
        insert_query = sql.SQL("""
            INSERT INTO realty_data (
                location, segment, project, building_number, rooms_numbers, 
                price, living_area, outdoor_space_type, surface_area_of_outdoor_space, 
                floor, leasehold_price, furnishing_cost, orientation, service_cost, 
                parking, website, {column_name}
            ) VALUES (
                %(location)s, %(segment)s, %(project)s, %(building_number)s, %(rooms_numbers)s, 
                %(price)s, %(living_area)s, %(outdoor_space_type)s, %(surface_area_of_outdoor_space)s, 
                %(floor)s, %(leasehold_price)s, %(furnishing_cost)s, %(orientation)s, %(service_cost)s, 
                %(parking)s, %(website)s, %({column_name})s
            )
        """).format(column_name=sql.SQL(state_table))

        # Execute the query with the data
        cursor.execute(insert_query, data)
        connection.commit()
    except psycopg2.Error as e:
        print('Insert data error', e)
        connection.rollback()
    finally:
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
    data_dict = {
        "location": "Amsterdam",
        "segment": "Huur",
        "project": "PLS",
        "building_number": "B123",
        "rooms_numbers": 3,
        "price": 1500,
        "living_area": 75,
        "outdoor_space_type": "Balcony",
        "surface_area_of_outdoor_space": 20,
        "floor": 2,
        "leasehold_price": None,
        "furnishing_cost": None,
        "orientation": "North",
        "service_cost": None,
        "parking": "Yes",
        "website": "https://example.com",
        f"state_for_{today_column_name}": "Segment data for today"
    }
    table_name = "realty_data"
    get_columns_sorted_by_creation(table_name)
