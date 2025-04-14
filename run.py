import os
import socket
from app import create_app

# Replace the problematic getfqdn function
original_getfqdn = socket.getfqdn

def safe_getfqdn(name=''):
    try:
        return original_getfqdn(name)
    except UnicodeDecodeError:
        return 'localhost'

# Apply monkey patch
socket.getfqdn = safe_getfqdn

# Create the app
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    # run_simple('localhost', 5000, app, use_debugger=True, use_reloader=True) 
    app.run(host='0.0.0.0', port=5000, debug=True) 