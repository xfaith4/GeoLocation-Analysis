# GeoLocation Analysis - GNSS Data Visualization

A web application for analyzing and visualizing GNSS (Global Navigation Satellite System) module data with support for high-precision positioning techniques including RTK, SBAS, and PPP.

## Features

- **📊 Enhanced Statistics Dashboard**: 8+ comprehensive metrics including signal quality, position spread, altitude range, and satellite counts
- **📈 Fix Type Distribution**: Visual breakdown of positioning accuracy with detailed explanations
- **🗺️ Interactive Map**: Visualize position data on an interactive map with color-coded fix quality indicators
- **📋 Data Tables**: View detailed GNSS metrics including fix type, satellite count, HDOP, and more
- **🔄 Real-time Processing**: Parse NMEA sentences (GGA, RMC, GSA, GSV, etc.) in real-time
- **📤 File Upload**: Analyze your own GNSS log files instantly

## What to Expect

When you run this application, you'll see:

### 1. **Summary Statistics** (8 Cards)

- **Total Sentences**: Count of all parsed NMEA messages
- **Avg Satellites**: Average number of satellites in view with min/max range
- **Primary Fix Type**: Most common positioning mode (RTK Fixed, RTK Float, GPS Fix, etc.)
- **Avg HDOP**: Horizontal Dilution of Precision with range (lower is better)
- **Altitude Range**: Elevation variation across all measurements
- **Signal Quality**: Percentage of high-precision fixes (RTK/DGPS)
- **Position Spread**: Geographic coverage area in meters or centimeters
- **Data Points**: Number of position fixes and data types

### 2. **Fix Type Distribution**

A visual bar chart showing the breakdown of positioning accuracy types:

- **RTK Fixed** (Green): Centimeter-level accuracy (~1-2 cm) - Best
- **RTK Float** (Cyan): Decimeter-level accuracy (~10-50 cm) - Good
- **DGPS Fix** (Teal): Meter-level accuracy (~1-5 m) - Better than standard
- **GPS Fix** (Yellow): Standard accuracy (~3-10 m) - Baseline
- **No Fix** (Red): Position unavailable

### 3. **Position Visualization**

Interactive map with color-coded markers showing position quality at each measurement point.

### 4. **Data Tables**

Detailed tables for GGA, RMC, and GSA NMEA sentence types with all positioning parameters.

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

**Step 1:** Clone the repository:

```bash
git clone https://github.com/xfaith4/GeoLocation-Analysis.git
cd GeoLocation-Analysis
```

**Step 2:** Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Step 3:** Install dependencies:

```bash
pip install -r requirements.txt
```

This will install:

- Flask 3.0.0 - Web framework
- Werkzeug 3.0.3 - WSGI utilities
- pynmea2 1.19.0 - NMEA sentence parser

### Running the Application

**Development Mode:**

Start the web server:

```bash
python app.py
```

You should see output like:

``` url
Starting GNSS Data Visualization Server...
Navigate to http://localhost:5006
⚠️  Running in DEBUG mode - DO NOT use in production!
 * Running on http://127.0.0.1:5006
```

Open your browser and navigate to:

``` url
http://localhost:5006
```

**Expected Outcome:**

- The application will automatically load and display sample GNSS data from `sample_data/sample_gnss.nmea`
- You'll see 8 statistics cards with real-time metrics
- A fix type distribution chart will show positioning accuracy breakdown
- Interactive map (if Leaflet loads) or data tables will display position information
- You can upload your own `.nmea`, `.txt`, or `.log` files using the upload section

**Production Deployment:**

For production deployment, disable debug mode:

```bash
export FLASK_ENV=production
python app.py
```

Or use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
<<<<<<< HEAD
python app.py
=======
gunicorn app:app -b 0.0.0.0:5006 -w 4
>>>>>>> 1696801952bcf73e487b05cc6b7144270a621a21
```

The `-w 4` flag runs 4 worker processes for better performance.

### Verification Steps

After starting the application, verify it's working correctly:

1. **Check the server is running:**

   ```bash
   curl http://localhost:5006/api/stats
   ```

   You should see JSON with statistics like `total_sentences`, `avg_satellites`, `fix_types`, etc.

2. **Access the web interface:**
   Open `http://localhost:5006` in your browser

3. **Verify data is loading:**
   - Statistics cards should show numerical values (not "-")
   - Fix type distribution should display at least one bar
   - GGA data table should contain at least one row of data

### Troubleshooting

**Issue:** Port 5006 already in use

```bash
# Find process using port 5006
lsof -i :5006  # On Linux/Mac
netstat -ano | findstr :5006  # On Windows

# Kill the process or change port in app.py (line 116)
```

**Issue:** Map not displaying

- The map requires internet access to load Leaflet library
- Data tables will still work without the map
- Check browser console for network errors

**Issue:** No data showing

- Verify `sample_data/sample_gnss.nmea` exists
- Check server console for parsing errors
- Try uploading a valid NMEA file manually

## Project Structure

```diagram
GeoLocation-Analysis/
├── app.py                  # Main Flask application
├── gnss_parser.py         # GNSS data parsing utilities
├── requirements.txt       # Python dependencies
├── static/               # Static assets (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/            # HTML templates
│   └── index.html
├── sample_data/          # Sample GNSS data files
│   └── sample_gnss.nmea
└── README.md            # This file
```

## GNSS Data Formats Supported

- **NMEA 0183**: GGA, RMC, GSA, GSV, VTG sentences
- Support for RTK fix types (Float/Fixed)
- Satellite information and signal quality

## Mission Statement

For detailed information about the project goals and analysis methodology, see [MissionsStatement.md](MissionsStatement.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details
