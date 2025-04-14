import sqlite3

def main():
    print("Starting direct database fix...")
    
    conn = sqlite3.connect('instance/campus.db')
    cursor = conn.cursor()
    
    # Turn off foreign key constraints
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Check if departments table exists and backup
    departments = []
    try:
        cursor.execute("SELECT * FROM departments")
        departments = cursor.fetchall()
        print(f"Backed up {len(departments)} departments")
    except:
        print("Could not find departments table or it's empty")
    
    # Get column names
    columns = []
    try:
        cursor.execute("PRAGMA table_info(departments)")
        columns = cursor.fetchall()
        print(f"Current columns: {[col[1] for col in columns]}")
    except:
        print("Could not get column info")
    
    # Re-create the departments table
    try:
        # Drop the existing table
        cursor.execute("DROP TABLE IF EXISTS departments")
        print("Dropped old departments table")
        
        # Create the new table with contact column
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
        print("Created new departments table with contact column")
        
        # Insert backed up data if available
        if departments and columns:
            col_names = [col[1] for col in columns]
            contact_index = -1
            if 'contact' in col_names:
                contact_index = col_names.index('contact')
            
            for dept in departments:
                contact_value = dept[contact_index] if contact_index >= 0 and contact_index < len(dept) else ''
                name_index = col_names.index('name') if 'name' in col_names else 1
                code_index = col_names.index('code') if 'code' in col_names else 2
                desc_index = col_names.index('description') if 'description' in col_names else 3
                
                name = dept[name_index] if name_index < len(dept) else ''
                code = dept[code_index] if code_index < len(dept) else ''
                description = dept[desc_index] if desc_index < len(dept) else ''
                
                cursor.execute('''
                INSERT INTO departments (name, code, contact, description)
                VALUES (?, ?, ?, ?)
                ''', (name, code, contact_value, description))
            
            print(f"Restored {len(departments)} departments with contact field")
    except Exception as e:
        print(f"Error recreating table: {e}")
    
    # Turn foreign key constraints back on
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database fix completed")

if __name__ == "__main__":
    main() 