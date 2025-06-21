import sqlite3

def run_query(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Query failed: {e}")
        return None

def sample_queries():
    return {
        '1': {
            'desc': 'Join stats with events by year (2021+)',
            'sql': '''
                SELECT s.year, s.league, s.leader_value, e.event_type, e.description
                FROM stats s
                JOIN events e ON s.year = e.year
                WHERE s.year >= 2021
                ORDER BY s.year DESC;
            '''
        },
        '2': {
            'desc': 'Home run leaders in American League after 2020',
            'sql': '''
                SELECT year, league, leader_value
                FROM stats
                WHERE league = 'American League' AND year > 2020;
            '''
        },
        '3': {
            'desc': 'All events for 2023',
            'sql': '''
                SELECT * FROM events WHERE year = 2023;
            '''
        }
    }

def main():
    db_path = "mlb_history.db"
    queries = sample_queries()

    print("\nAvailable Queries:")
    for key, val in queries.items():
        print(f"{key}. {val['desc']}")

    choice = input("\nSelect a query number: ").strip()
    if choice in queries:
        result = run_query(db_path, queries[choice]['sql'])
        if result is not None:
            print(result)
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    import pandas as pd
    main()
