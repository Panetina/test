import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'Ko-fi Goal API is running! Use /goal endpoint.'

@app.route('/goal')
def get_goal():
    try:
        response = requests.get('https://ko-fi.com/panyel', timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        goal_element = soup.find('span', {'id': 'profileGoalTotal'})
        if goal_element:
            text = goal_element.text
            match = re.search(r'€?(\d+(?:\.\d+)?).*€?(\d+(?:\.\d+)?)', text)
            if match:
                current = float(match.group(1))
                goal = float(match.group(2))
                percentage = (current / goal) * 100
                return jsonify({
                    'success': True,
                    'current': current,
                    'goal': goal,
                    'percentage': percentage
                })
        
        return jsonify({'success': False, 'error': 'Goal not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
