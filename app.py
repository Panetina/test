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
        url = 'https://ko-fi.com/panyel'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the span with class="kfds-font-bold" that contains the percentage
        # In your scraped HTML, it's: <span class="kfds-font-bold">2% </span>
        percent_span = soup.find('span', class_='kfds-font-bold')
        if percent_span:
            percent_text = percent_span.get_text(strip=True)
            match = re.search(r'(\d+(?:\.\d+)?)%', percent_text)
            if match:
                percent = float(match.group(1))
                # Now find the goal amount from the span with id="profileGoalTotal"
                goal_span = soup.find('span', id='profileGoalTotal')
                if goal_span:
                    goal_text = goal_span.get_text()
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

        # Fallback: search the entire page text
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

        # Default if nothing found
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
