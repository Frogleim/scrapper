import psycopg2
import pandas as pd

# Database connection parameters
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": "5433"
}


def fetch_data_from_postgres(query):
    """Fetch data from PostgreSQL database using the provided query."""
    try:
        # Connect to the database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Fetch column names
        column_names = [desc[0] for desc in cursor.description]

        # Convert to a pandas DataFrame
        df = pd.DataFrame(rows, columns=column_names)

        return df

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


def save_to_excel(df, filename):
    """Save the DataFrame to an Excel file."""
    df.to_excel(filename, index=False, engine='openpyxl')


def run():
    # Define your SQL query
    query = "SELECT * FROM realty_data;"  # Replace with your query

    # Fetch data from PostgreSQL
    data = fetch_data_from_postgres(query)

    # Save the data to an Excel file
    if data is not None:
        save_to_excel(data, 'realty_data.xlsx')
        print("Data has been saved to 'realty_data.xlsx'.")

if __name__ == "__main__":
    run()
