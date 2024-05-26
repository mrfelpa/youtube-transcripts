import sqlite3
from sqlite3 import Error
import argparse

def create_tables(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print("Database connection established")

        conn.execute("DROP TABLE IF EXISTS transcripts")
        conn.execute("DROP TABLE IF EXISTS processed")
        conn.execute("DROP INDEX IF EXISTS index_transcripts_title")
        conn.execute('CREATE TABLE transcripts (title TEXT, url TEXT, description TEXT)')
        conn.execute('CREATE TABLE processed (url TEXT)')
        conn.execute('CREATE INDEX IF NOT EXISTS index_transcripts_title ON transcripts(title)')
        conn.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

def main():
    parser = argparse.ArgumentParser(description='SQLite Database Setup')
    parser.add_argument('--db', default='mc_transcripts.db', help='SQLite database file')
    args = parser.parse_args()

    create_tables(args.db)

if __name__ == "__main__":
    main()
