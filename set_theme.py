import os
from app import create_app, db
from app.models.system import SystemSettingService

# Create the application context
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    # 设置系统名称
    site_name = "智证融合"
    SystemSettingService.set('site_name', site_name, 'string', '系统名称')
    print(f"系统名称设置为: {site_name}")
    
    # Set the theme color
    theme_color = "#0d6efd"  # Default blue theme
    SystemSettingService.set('theme_color', theme_color, 'string', '主题颜色')
    print(f"Theme color set to: {theme_color}")
    
    # Check if the settings are accessible
    all_settings = SystemSettingService.get_all()
    print("Current settings:")
    for key, value in all_settings.items():
        print(f"  {key}: {value}") 