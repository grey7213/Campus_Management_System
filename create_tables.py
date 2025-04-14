import os
from app import create_app, db

# Create the application context
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Tables created successfully!")
    
    # Import after tables are created to avoid circular import issues
    from app.models.system import SystemSetting, init_default_settings
    print("Initializing default settings...")
    init_default_settings()
    print("Default settings initialized!") 