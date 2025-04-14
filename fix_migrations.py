import os
import shutil
from datetime import datetime

def main():
    print("Preparing to fix migrations...")
    
    # 1. Create backups of migrations and database
    migrations_dir = 'migrations'
    if os.path.exists(migrations_dir):
        backup_dir = f"{migrations_dir}_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copytree(migrations_dir, backup_dir)
        print(f"Backed up migrations to {backup_dir}")
    
    db_file = 'data-dev.sqlite'
    if os.path.exists(db_file):
        backup_file = f"{db_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(db_file, backup_file)
        print(f"Backed up database to {backup_file}")
    
    # 2. Instructions for manual steps
    print("\nTo fix the migrations, follow these steps:")
    print("\n1. Stop all Flask applications")
    print("2. Remove the migrations directory:")
    print("   rm -rf migrations")
    print("\n3. Create a fresh migrations repository:")
    print("   flask db init")
    print("\n4. Uncomment the contact field in app/models/teacher.py:")
    print("   # contact = db.Column(db.String(100), nullable=True)  →  contact = db.Column(db.String(100), nullable=True)")
    print("\n5. Uncomment the contact field in the routes in app/routes/admin.py")
    print("\n6. Generate the initial migration:")
    print("   flask db migrate -m \"initial migration\"")
    print("\n7. Apply the migration:")
    print("   flask db upgrade")
    print("\n8. Start the Flask application:")
    print("   flask run")
    
    print("\nThese steps will reset your migration history and ensure the database and models are in sync.")

if __name__ == "__main__":
    main() 