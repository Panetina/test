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
        response = requests.get('https://ko-fi.com/panyel', timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the goal label element
        goal_label = soup.find('span', {'id': 'profileGoalTotal'})
        if not goal_label:
            # Fallback: look for any element containing "of €" and "goal"
            goal_label = soup.find(string=re.compile(r'of\s*€\d+\s*goal', re.IGNORECASE))
        
        if goal_label:
            text = goal_label.get_text() if hasattr(goal_label, 'get_text') else str(goal_label)
            # Example text: "0% of €50 goal" or "25% of €50 goal"
            match = re.search(r'(\d+(?:\.\d+)?)%\s+of\s+€(\d+(?:\.\d+)?)', text)
            if match:
                percent = float(match.group(1))
                goal = float(match.group(2))
                # We don't have the current amount, but we can compute it if needed
                current = (percent / 100) * goal
                return jsonify({
                    'success': True,
                    'percentage': percent,
                    'current': round(current, 2),
                    'goal': goal
                })
        
        # If everything fails, return a default
        return jsonify({
            'success': True,
            'percentage': 0,
            'current': 0,
            'goal': 50,
            'message': 'Goal text not found on page'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
