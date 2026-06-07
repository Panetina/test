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
        # Fetch your Ko-fi goal page
        response = requests.get('https://ko-fi.com/panyel/goal', timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the goal percentage text
        goal_text = None
        
        # Method 1: Look for the progress bar text
        progress_bar = soup.find('div', {'class': 'progress-bar'})
        if progress_bar:
            width = progress_bar.get('style', '')
            match = re.search(r'width:\s*(\d+(?:\.\d+)?)%', width)
            if match:
                percentage = float(match.group(1))
                return jsonify({
                    'success': True,
                    'percentage': percentage,
                    'message': f'Goal is {percentage}% complete'
                })
        
        # Method 2: Look for the goal label text
        goal_label = soup.find('span', {'class': 'goal-label'})
        if goal_label:
            goal_text = goal_label.text
        
        # Method 3: Look for any text with the pattern
        if not goal_text:
            all_text = soup.get_text()
            match = re.search(r'(\d+(?:\.\d+)?)%', all_text)
            if match:
                percentage = float(match.group(1))
                return jsonify({
                    'success': True,
                    'percentage': percentage,
                    'message': 'Goal progress found'
                })
        
        # If we found text but no percentage yet
        if goal_text:
            match = re.search(r'(\d+(?:\.\d+)?)', goal_text)
            if match:
                percentage = float(match.group(1))
                return jsonify({
                    'success': True,
                    'percentage': percentage,
                    'raw_text': goal_text
                })
        
        # Default response if no goal is set up
        return jsonify({
            'success': True,
            'percentage': 0,
            'message': 'No active goal found. Set up a goal on Ko-fi!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
