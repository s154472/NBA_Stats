from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import os
import traceback

# Ensure the directory containing your original script is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import your existing NBA stats tracker class
from NBA_Scrape import NBAPlayerStatsTracker

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the tracker
tracker = NBAPlayerStatsTracker()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_player_stats', methods=['POST'])
def get_player_stats():
    # Get data from the request
    data = request.json
    player_name = data.get('player_name')
    stat_type = data.get('stat_type')

    print(f"Received request: player_name={player_name}, stat_type={stat_type}")

    if not player_name or not stat_type:
        return jsonify({'error': 'Missing player name or stat type'}), 400

    try:
        # Capture print output
        import io
        import sys

        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        # Get player stats
        df = tracker.get_player_stats(player_name, stat_type)

        # Get the captured output
        output = captured_output.getvalue()
        sys.stdout = old_stdout

        # Convert DataFrame to list of dictionaries for JSON serialization
        if not df.empty:
            # Convert GAME_DATE to string to ensure JSON serialization
            df['GAME_DATE'] = df['GAME_DATE'].astype(str)
            stats_data = df[['GAME_DATE', tracker.stat_mapping[stat_type]]].to_dict('records')
            return jsonify({
                'output': output,  # You can remove this in production
                'stats': stats_data
            })
        else:
            return jsonify({'error': 'No stats found for the player'}), 404

    except Exception as e:
        # Print full traceback for server-side debugging
        print("Full error traceback:")
        traceback.print_exc()
        
        # Return detailed error information
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
