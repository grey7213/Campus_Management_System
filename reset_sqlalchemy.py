from app import create_app, db
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
import os

def main():
    print("Starting SQLAlchemy metadata reset...")
    
    # Get the app's database URI
    app = create_app('default')
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database URI: {db_uri}")
    
    # Create a fresh engine
    engine = create_engine(db_uri)
    
    with app.app_context():
        # Clear SQLAlchemy's metadata
        db.Model.metadata.clear()
        
        # Reflect current database structure
        db.Model.metadata.reflect(bind=engine)
        
        # Check if departments table is in metadata
        if 'departments' in db.Model.metadata.tables:
            dept_table = db.Model.metadata.tables['departments']
            print(f"Departments table columns: {[c.name for c in dept_table.columns]}")
            
            # Check if contact column is in the table
            if 'contact' in dept_table.columns:
                print("Contact column found in metadata")
            else:
                print("Contact column NOT found in metadata")
                
                # Force reflection of just the departments table
                meta = MetaData()
                meta.reflect(bind=engine, only=['departments'])
                
                if 'departments' in meta.tables:
                    dept_table = meta.tables['departments']
                    print(f"Re-reflected columns: {[c.name for c in dept_table.columns]}")
                else:
                    print("Failed to re-reflect departments table")
        else:
            print("Departments table not found in metadata")
        
        print("\nRESET DATABASE CONNECTIONS:")
        print("1. Stop all Flask applications")
        print("2. Restart your Flask server")
        print("3. Try adding departments again")
        
        print("\nAlternative fix:")
        print("1. Modify the Department model to not use the 'contact' field temporarily")
        print("2. Fix the database structure permanently by recreating migrations")

if __name__ == "__main__":
    main() 