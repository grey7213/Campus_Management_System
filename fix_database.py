import sqlite3
import os

def main():
    # Define path for the database
    db_path = 'instance/campus.db'
    
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    try:
        # Connect to the database (creates it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if departments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'")
        if not cursor.fetchone():
            # Create departments table with contact column
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
            conn.commit()
            print("Departments table created with contact column")
        else:
            # Check if contact column exists in departments table
            cursor.execute("PRAGMA table_info(departments)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'contact' not in column_names:
                # Add contact column to departments table
                cursor.execute("ALTER TABLE departments ADD COLUMN contact VARCHAR(100)")
                conn.commit()
                print("Contact column added successfully to departments table")
            else:
                print("Contact column already exists in departments table")
        
        # Close connection
        conn.close()
        print("Database updated successfully")
    
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    main() 