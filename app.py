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
        # Fetch the main page (not /goal)
        url = 'https://ko-fi.com/panyel'
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the percentage text inside a span with class 'kfds-font-bold'
        # It appears as "2% " (with a space)
        percent_span = soup.find('span', class_='kfds-font-bold')
        if percent_span:
            text = percent_span.get_text(strip=True)
            # Extract the number (e.g., "2%" -> 2)
            match = re.search(r'(\d+(?:\.\d+)?)%', text)
            if match:
                percent = float(match.group(1))
                # Also extract the goal amount from the goal label
                goal_label = soup.find('span', id='profileGoalTotal')
                if goal_label:
                    goal_text = goal_label.get_text()
                    goal_match = re.search(r'€(\d+)', goal_text)
                    if goal_match:
                        goal = float(goal_match.group(1))
                        current = (percent / 100) * goal
                        return jsonify({
                            'success': True,
                            'percentage': percent,
                            'current': round(current, 2),
                            'goal': goal
                        })
        # If the above fails, fallback to searching the whole page text
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
        # If still nothing, return a default (goal not active)
        return jsonify({
            'success': True,
            'percentage': 0,
            'current': 0,
            'goal': 50,
            'message': 'No active goal found on Ko-fi page'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
