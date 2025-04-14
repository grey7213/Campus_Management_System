import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Campus Management System is running!"

@app.route('/test')
def test():
    return "Test successful!"

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True) 