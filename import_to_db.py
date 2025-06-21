import sqlite3
import pandas as pd
import os

def import_csv_to_db(db_path, csv_folder):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    files = {
        'years': 'years.csv',
        'stats': 'stats.csv',
        'events': 'events.csv'
    }

    for table, filename in files.items():
        path = os.path.join(csv_folder, filename)
        if not os.path.exists(path):
            print(f"File not found: {filename}")
            continue

        df = pd.read_csv(path)

        # Log before transformation
        print("Before transformation:")
        print("Showing first 3 rows:\n", df.head(3))
        print("Showing Column Data Types\n", df.dtypes)
        print(f"Row count: {len(df)}")
        print(f"Missing values:\n{df.isnull().sum()}")

        # clean missing value
        if table == 'years':
            df = df.dropna(subset=['year', 'league', 'url'])  # Drop rows with missing critical columns
        elif table == 'stats':
            df = df.dropna(subset=['year', 'league', 'leader_value'])  # Drop rows with missing critical columns
            df['leader_value'] = df['leader_value'].fillna(0)  # Fill missing leader_value with 0 if not dropped
        elif table == 'events':
            df = df.dropna(subset=['year', 'event_type', 'description'])  # Drop rows with missing critical columns

        # remove duplicate:
        initial_rows = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_rows:
            print(f"Removed {initial_rows - len(df)} duplicate rows")

        # validate and clean data
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            df = df[df['year'].notnull() & (df['year'].between(2000, 2025))]
            df['year'] = df['year'].astype(int)
        if 'leader_value' in df.columns:
            df['leader_value'] = pd.to_numeric(df['leader_value'], errors='coerce')
            df = df[df['leader_value'].notnull() & (df['leader_value'] >= 0)]
            df['leader_value'] = df['leader_value'].astype(int)
        if 'team_count' in df.columns:
            df['team_count'] = pd.to_numeric(df['team_count'], errors='coerce')
            df = df[df['team_count'].notnull() & (df['team_count'] > 0)]
            df['team_count'] = df['team_count'].astype(int)

        # Apply transformations (ensure proper data types)
        if 'year' in df.columns:
            df['year'] = df['year'].astype(int)  # Convert year to integer

        # Log after transformation
        print("After transformation:")
        print("Showing first 3 rows:\n", df.head(3))
        print("Showing Data types:\n", df.dtypes)
        print(f"Row count: {len(df)}")
        print(f"Missing values:\n{df.isnull().sum()}")

        # Save to database
        try:
            df.to_sql(table, conn, if_exists='replace', index=False)
            print(f"Imported {filename} into table '{table}' with {len(df)} rows")
        except Exception as e:
            print(f"Error importing {filename} to table '{table}': {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    import_csv_to_db("mlb_history.db", "data")
