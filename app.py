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
        
        # Try multiple methods to find the percentage
        
        # Method 1: Look for the progress bar width
        progress_bar = soup.find('div', class_='progress-bar')
        if progress_bar:
            style = progress_bar.get('style', '')
            match = re.search(r'width:\s*(\d+(?:\.\d+)?)%', style)
            if match:
                percent = float(match.group(1))
                # Get goal amount
                goal_label = soup.find('span', {'id': 'profileGoalTotal'})
                goal = 50
                if goal_label:
                    text = goal_label.get_text()
                    match_goal = re.search(r'€(\d+)', text)
                    if match_goal:
                        goal = float(match_goal.group(1))
                current = (percent / 100) * goal
                return jsonify({
                    'success': True,
                    'percentage': percent,
                    'current': round(current, 2),
                    'goal': goal
                })
        
        # Method 2: Look for percentage text
        all_text = soup.get_text()
        match = re.search(r'(\d+(?:\.\d+)?)%\s+of\s+€(\d+)', all_text)
        if match:
            percent = float(match.group(1))
            goal = float(match.group(2))
            current = (percent / 100) * goal
            return jsonify({
                'success': True,
                'percentage': percent,
                'current': round(current, 2),
                'goal': goal
            })
        
        # Method 3: Look for any percentage number near the goal
        goal_label = soup.find('span', {'id': 'profileGoalTotal'})
        if goal_label:
            text = goal_label.get_text()
            match = re.search(r'€(\d+)', text)
            if match:
                goal = float(match.group(1))
                # No percentage found, return 0
                return jsonify({
                    'success': True,
                    'percentage': 0,
                    'current': 0,
                    'goal': goal
                })
        
        return jsonify({
            'success': True,
            'percentage': 0,
            'current': 0,
            'goal': 50,
            'message': 'Could not parse goal data'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
