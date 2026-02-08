"""
Flask Web Application for GNSS Data Visualization
"""

from flask import Flask, render_template, jsonify, request
import os
from gnss_parser import GNSSParser

app = Flask(__name__)
parser = GNSSParser()

# Load sample data on startup
SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), 'sample_data', 'sample_gnss.nmea')
sample_data = []
sample_stats = {}

try:
    sample_data = parser.parse_file(SAMPLE_DATA_PATH)
    sample_stats = parser.get_summary_statistics(sample_data)
except Exception as e:
    print(f"Warning: Could not load sample data: {e}")


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/data')
def get_data():
    """API endpoint to get GNSS data"""
    return jsonify({
        'status': 'success',
        'data': sample_data,
        'count': len(sample_data)
    })


@app.route('/api/stats')
def get_stats():
    """API endpoint to get summary statistics"""
    return jsonify({
        'status': 'success',
        'stats': sample_stats
    })


@app.route('/api/positions')
def get_positions():
    """API endpoint to get position data for mapping"""
    gga_data = [d for d in sample_data if d.get('sentence_type') == 'GGA']
    positions = []
    
    for d in gga_data:
        if d.get('latitude') and d.get('longitude'):
            positions.append({
                'lat': d['latitude'],
                'lon': d['longitude'],
                'alt': d.get('altitude', 0),
                'fix_quality': d.get('fix_quality', 'Unknown'),
                'num_satellites': d.get('num_satellites', 0),
                'timestamp': d.get('timestamp', '')
            })
    
    return jsonify({
        'status': 'success',
        'positions': positions
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API endpoint to upload and parse a GNSS log file"""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    try:
        # Save temporarily and parse
        temp_path = os.path.join('/tmp', file.filename)
        file.save(temp_path)
        
        parsed_data = parser.parse_file(temp_path)
        stats = parser.get_summary_statistics(parsed_data)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            'status': 'success',
            'data': parsed_data,
            'stats': stats,
            'count': len(parsed_data)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/corrections', methods=['POST'])
def calculate_corrections():
    """API endpoint to calculate position corrections"""
    try:
        data = request.get_json()
        method = data.get('method', 'mean')
        weight_by_quality = data.get('weight_by_quality', True)
        
        # Use current sample data or uploaded data
        correction_info = parser.calculate_position_corrections(
            sample_data, 
            method=method,
            weight_by_quality=weight_by_quality
        )
        
        return jsonify({
            'status': 'success',
            'corrections': correction_info
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/apply_corrections', methods=['POST'])
def apply_corrections():
    """API endpoint to apply corrections to data"""
    try:
        data = request.get_json()
        method = data.get('method', 'mean')
        weight_by_quality = data.get('weight_by_quality', True)
        
        # Calculate corrections
        correction_info = parser.calculate_position_corrections(
            sample_data,
            method=method,
            weight_by_quality=weight_by_quality
        )
        
        if 'error' in correction_info:
            return jsonify({
                'status': 'error',
                'message': correction_info['error']
            }), 400
        
        # Apply corrections
        corrected_data = parser.apply_corrections_to_data(sample_data, correction_info)
        corrected_stats = parser.get_summary_statistics(corrected_data)
        
        return jsonify({
            'status': 'success',
            'data': corrected_data,
            'stats': corrected_stats,
            'corrections': correction_info
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    import os
    # Debug mode should only be enabled in development
    # Set FLASK_ENV=production for production deployment
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print("Starting GNSS Data Visualization Server...")
    print("Navigate to http://localhost:5006")
    
    if debug_mode:
        print("⚠️  Running in DEBUG mode - DO NOT use in production!")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5006)
