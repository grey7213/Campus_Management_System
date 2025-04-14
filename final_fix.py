import sqlite3
import os
import shutil
from datetime import datetime

def main():
    db_path = 'instance/campus.db'
    
    # Backup existing database if it exists
    if os.path.exists(db_path):
        backup_path = f"{db_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"Backed up existing database to {backup_path}")
    
    # Create or connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Turn off foreign key constraints
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Create departments table with contact column
    try:
        cursor.execute("DROP TABLE IF EXISTS departments")
        cursor.execute('''
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(64) UNIQUE,
            code VARCHAR(20) UNIQUE,
            contact VARCHAR(100),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        print("Created departments table with contact column")
        
        # Add a test department to verify
        cursor.execute('''
        INSERT INTO departments (name, code, contact, description)
        VALUES (?, ?, ?, ?)
        ''', ('计算机系', '501450', 'cs@example.com', 'Computer Science Department'))
        
        print("Added test department")
    except Exception as e:
        print(f"Error setting up departments table: {e}")
    
    # Turn foreign key constraints back on
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database setup completed")

if __name__ == "__main__":
    main() 