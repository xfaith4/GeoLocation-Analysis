# GeoLocation Analysis - GNSS Data Visualization

A web application for analyzing and visualizing GNSS (Global Navigation Satellite System) module data with support for high-precision positioning techniques.

## Features

- **Real-time GNSS Data Display**: View parsed GNSS module data in an intuitive web interface
- **Interactive Map**: Visualize position data on an interactive map
- **Data Tables**: View detailed GNSS metrics including fix type, satellite count, HDOP, and more
- **Support for Multiple Formats**: Parse NMEA sentences (GGA, RMC, GSA, GSV, etc.)
- **Performance Analysis**: Display key positioning metrics and statistics

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/xfaith4/GeoLocation-Analysis.git
cd GeoLocation-Analysis
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the web server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

The application will display sample GNSS data. You can upload your own GNSS log files for analysis.

## Project Structure

```
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
