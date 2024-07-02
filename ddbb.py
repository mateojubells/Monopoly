

import sqlite3
# SQLite3 database initialization
def init_db():
    conn = sqlite3.connect('monopoly.db')
    c = conn.cursor()
    
    # Create boards table
    c.execute('''
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            streets TEXT NOT NULL
        )
    ''')
    
    # Create extras table
    c.execute('''
        CREATE TABLE IF NOT EXISTS extras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            carts TEXT NOT NULL
        )
    ''')
    
    # Create custom_cards table
    c.execute('''
        CREATE TABLE IF NOT EXISTS custom_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT,
            station_image TEXT,
            company_name TEXT,
            company_image TEXT,
            luck_image TEXT,
            treasury_image TEXT,
            custom_card_image TEXT,
            custom_card_text TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()