from flask import Flask, render_template
from system_logger import collect_all_system_info
import json

app = Flask(__name__)

@app.route('/')
def home():
    # Collect system information
    system_data = collect_all_system_info()
    return render_template('index.html', data=system_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 