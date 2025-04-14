from wsgiref.simple_server import make_server
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Campus Management System is running!"

if __name__ == '__main__':
    # Use Python's built-in WSGI server instead of Werkzeug
    with make_server('', 5000, app) as httpd:
        print("Serving on port 5000...")
        httpd.serve_forever() 