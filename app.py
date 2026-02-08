"""
Flask Web Application for GNSS Data Visualization
"""

from flask import Flask, render_template, jsonify, request
import os
import requests
import math
from datetime import datetime
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


@app.route('/api/satellites')
def get_satellites():
    """API endpoint to get live satellite positions"""
    try:
        # Use N2YO API for satellite tracking
        # For this implementation, we'll use a simplified approach
        # In production, you would need an N2YO API key or use other satellite tracking services
        
        # Common GPS satellites (NORAD IDs)
        gps_satellites = [
            {'norad_id': 28361, 'name': 'GPS BIIA-14 (PRN 18)'},
            {'norad_id': 28474, 'name': 'GPS BIIR-2 (PRN 13)'},
            {'norad_id': 32384, 'name': 'GPS BIIR-13 (PRN 29)'},
            {'norad_id': 35752, 'name': 'GPS BIIF-1 (PRN 25)'},
            {'norad_id': 40105, 'name': 'GPS BIIF-4 (PRN 30)'},
        ]
        
        satellites = []
        
        # Calculate approximate satellite positions
        # This is a simplified calculation for demonstration
        # In production, use proper orbital mechanics or satellite tracking API
        current_time = datetime.utcnow()
        time_offset = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
        
        for i, sat_info in enumerate(gps_satellites):
            # Simple orbital simulation (not accurate, for demo only)
            # GPS satellites orbit at ~20,200 km altitude with 12-hour period
            orbital_period = 12 * 3600  # 12 hours in seconds
            angle = (time_offset + i * orbital_period / len(gps_satellites)) / orbital_period * 2 * math.pi
            
            # Calculate position (simplified circular orbit)
            inclination = 55 * math.pi / 180  # GPS orbit inclination
            lat = math.degrees(math.asin(math.sin(inclination) * math.sin(angle)))
            lon = math.degrees(angle) - 180 * (time_offset / (orbital_period / 2))
            
            # Normalize longitude to -180 to 180
            while lon > 180:
                lon -= 360
            while lon < -180:
                lon += 360
            
            satellites.append({
                'norad_id': sat_info['norad_id'],
                'name': sat_info['name'],
                'lat': lat,
                'lon': lon,
                'altitude': 20200,  # km
                'velocity': 3.87,  # km/s
                'visibility': 'Visible' if abs(lat) < 80 else 'Low visibility'
            })
        
        return jsonify({
            'status': 'success',
            'satellites': satellites,
            'timestamp': current_time.isoformat(),
            'note': 'Satellite positions are approximate and for demonstration purposes'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'satellites': []
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
