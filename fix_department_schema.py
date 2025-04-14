from app import create_app, db
from app.models.teacher import Department
import sqlite3

def main():
    print("Starting database fix...")
    
    # First check the database structure directly
    try:
        conn = sqlite3.connect('instance/campus.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(departments)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns in departments table: {column_names}")
        
        # If contact column doesn't exist, try to add it
        if 'contact' not in column_names:
            try:
                print("Adding contact column directly with SQLite...")
                cursor.execute("ALTER TABLE departments ADD COLUMN contact VARCHAR(100)")
                conn.commit()
                print("Contact column added successfully using SQLite")
            except Exception as e:
                print(f"Error adding column with SQLite: {e}")
        else:
            print("Contact column already exists in SQLite schema")
            
        conn.close()
    except Exception as e:
        print(f"Error checking database with SQLite: {e}")
    
    # Create Flask app context and try to rebuild the table if needed
    try:
        app = create_app('default')
        with app.app_context():
            print("Attempting to fix with SQLAlchemy...")
            
            # Backup any existing departments
            existing_departments = []
            try:
                existing_departments = Department.query.all()
                print(f"Found {len(existing_departments)} existing departments to backup")
            except Exception as e:
                print(f"Error getting existing departments: {e}")
            
            # If we need to recreate the table
            if existing_departments:
                departments_data = []
                for dept in existing_departments:
                    departments_data.append({
                        'name': dept.name,
                        'code': dept.code,
                        'description': dept.description,
                        'contact': getattr(dept, 'contact', '')
                    })
                
                print("Backed up department data")
                
                # This is a drastic approach but might be necessary
                # Use SQLite to rebuild the table with the correct schema
                try:
                    conn = sqlite3.connect('instance/campus.db')
                    cursor = conn.cursor()
                    
                    # Disable foreign key constraints temporarily
                    cursor.execute("PRAGMA foreign_keys = OFF")
                    
                    # Backup teachers table that references departments
                    cursor.execute("SELECT * FROM teachers")
                    teachers = cursor.fetchall()
                    
                    # Create temporary table for departments
                    cursor.execute('''
                    CREATE TABLE departments_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(64) UNIQUE,
                        code VARCHAR(20) UNIQUE,
                        contact VARCHAR(100),
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    ''')
                    
                    # Drop the old table
                    cursor.execute("DROP TABLE departments")
                    
                    # Rename the new table to the old name
                    cursor.execute("ALTER TABLE departments_new RENAME TO departments")
                    
                    # Restore department data
                    for dept_data in departments_data:
                        cursor.execute(
                            "INSERT INTO departments (name, code, contact, description) VALUES (?, ?, ?, ?)",
                            (dept_data['name'], dept_data['code'], dept_data['contact'], dept_data['description'])
                        )
                    
                    conn.commit()
                    print("Departments table recreated successfully")
                    
                    # Re-enable foreign key constraints
                    cursor.execute("PRAGMA foreign_keys = ON")
                    conn.close()
                except Exception as e:
                    print(f"Error recreating departments table: {e}")
            
            print("Database fix completed")
    except Exception as e:
        print(f"Error in Flask app context: {e}")

if __name__ == "__main__":
    main() 