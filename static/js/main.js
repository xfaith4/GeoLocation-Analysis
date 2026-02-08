// GNSS Data Visualization JavaScript

// Global variables
let map;
let markers = [];
let currentData = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadData();
    setupEventListeners();
});

// Initialize Leaflet map
function initializeMap() {
    try {
        // Check if Leaflet is available
        if (typeof L === 'undefined') {
            console.warn('Leaflet not loaded, map will not be available');
            document.getElementById('map').innerHTML = '<div style="text-align: center; padding: 50px; color: #666;">Map visualization requires Leaflet library. Data tables are still available below.</div>';
            return;
        }
        
        // Default center (San Francisco Bay Area based on sample data)
        map = L.map('map').setView([37.387458, -121.972360], 13);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(map);
    } catch (error) {
        console.error('Error initializing map:', error);
        document.getElementById('map').innerHTML = '<div style="text-align: center; padding: 50px; color: #666;">Map unavailable. Data tables are still available below.</div>';
    }
}

// Load GNSS data from API
async function loadData() {
    try {
        // Load statistics
        const statsResponse = await fetch('/api/stats');
        const statsData = await statsResponse.json();
        
        if (statsData.status === 'success') {
            updateStatistics(statsData.stats);
        }
        
        // Load data
        const dataResponse = await fetch('/api/data');
        const data = await dataResponse.json();
        
        if (data.status === 'success') {
            currentData = data.data;
            updateTables(currentData);
        }
        
        // Load positions for map
        const positionsResponse = await fetch('/api/positions');
        const positionsData = await positionsResponse.json();
        
        if (positionsData.status === 'success') {
            plotPositions(positionsData.positions);
        }
        
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Update statistics cards
function updateStatistics(stats) {
    document.getElementById('total-sentences').textContent = stats.total_sentences || 0;
    document.getElementById('avg-satellites').textContent = 
        stats.avg_satellites ? stats.avg_satellites.toFixed(1) : '-';
    
    // Satellite range
    if (stats.min_satellites !== undefined && stats.max_satellites !== undefined) {
        document.getElementById('satellite-range').textContent = 
            `Range: ${stats.min_satellites}-${stats.max_satellites}`;
    }
    
    // Display most common fix type
    if (stats.fix_types) {
        const fixTypes = Object.entries(stats.fix_types);
        if (fixTypes.length > 0) {
            const mostCommon = fixTypes.reduce((a, b) => a[1] > b[1] ? a : b);
            document.getElementById('fix-quality').textContent = mostCommon[0];
        }
    }
    
    // HDOP statistics
    document.getElementById('avg-hdop').textContent = 
        stats.avg_hdop ? stats.avg_hdop.toFixed(2) : '-';
    
    if (stats.min_hdop !== undefined && stats.max_hdop !== undefined) {
        document.getElementById('hdop-range').textContent = 
            `Range: ${stats.min_hdop.toFixed(2)}-${stats.max_hdop.toFixed(2)}`;
    }
    
    // Altitude statistics
    if (stats.altitude_range !== undefined) {
        document.getElementById('altitude-range').textContent = 
            `${stats.altitude_range.toFixed(1)} m`;
        document.getElementById('altitude-avg').textContent = 
            `Avg: ${stats.avg_altitude.toFixed(1)} m`;
    } else {
        document.getElementById('altitude-range').textContent = '-';
        document.getElementById('altitude-avg').textContent = '-';
    }
    
    // Signal quality
    if (stats.signal_quality_percent !== undefined) {
        document.getElementById('signal-quality').textContent = 
            `${stats.signal_quality_percent}%`;
    } else {
        document.getElementById('signal-quality').textContent = '-';
    }
    
    // Position spread
    if (stats.position_spread_meters !== undefined) {
        const spread = stats.position_spread_meters;
        if (spread < 1) {
            document.getElementById('position-spread').textContent = 
                `${(spread * 100).toFixed(1)} cm`;
        } else if (spread < 1000) {
            document.getElementById('position-spread').textContent = 
                `${spread.toFixed(1)} m`;
        } else {
            document.getElementById('position-spread').textContent = 
                `${(spread / 1000).toFixed(2)} km`;
        }
    } else {
        document.getElementById('position-spread').textContent = '-';
    }
    
    // Data points
    document.getElementById('data-points').textContent = stats.gga_count || 0;
    document.getElementById('fix-breakdown').textContent = 
        `${stats.gga_count || 0} GGA, ${stats.rmc_count || 0} RMC`;
    
    // Update fix type distribution chart
    updateFixDistribution(stats.fix_types, stats.fix_percentages);
}

// Update fix type distribution visualization
function updateFixDistribution(fixTypes, fixPercentages) {
    const barsContainer = document.getElementById('fix-bars');
    barsContainer.innerHTML = '';
    
    if (!fixTypes || Object.keys(fixTypes).length === 0) {
        barsContainer.innerHTML = '<p class="loading">No fix type data available</p>';
        return;
    }
    
    // Define colors for each fix type
    const fixColors = {
        'RTK Fixed': '#28a745',
        'RTK Float': '#17a2b8',
        'DGPS Fix': '#20c997',
        'GPS Fix': '#ffc107',
        'No Fix': '#dc3545',
        'Estimated': '#fd7e14',
        'PPS Fix': '#6610f2',
        'Manual': '#6c757d',
        'Simulation': '#e83e8c'
    };
    
    // Sort by count (descending)
    const sortedFixTypes = Object.entries(fixTypes).sort((a, b) => b[1] - a[1]);
    
    sortedFixTypes.forEach(([fixType, count]) => {
        const percentage = fixPercentages ? fixPercentages[fixType] : ((count / Object.values(fixTypes).reduce((a, b) => a + b, 0)) * 100).toFixed(1);
        const color = fixColors[fixType] || '#6c757d';
        
        const barWrapper = document.createElement('div');
        barWrapper.className = 'fix-bar-wrapper';
        
        barWrapper.innerHTML = `
            <div class="fix-bar-label">
                <span class="fix-type-name">${fixType}</span>
                <span class="fix-count">${count} (${percentage}%)</span>
            </div>
            <div class="fix-bar-track">
                <div class="fix-bar-fill" style="width: ${percentage}%; background-color: ${color};"></div>
            </div>
        `;
        
        barsContainer.appendChild(barWrapper);
    });
}

// Plot positions on the map
function plotPositions(positions) {
    // Skip if map is not initialized
    if (!map || typeof L === 'undefined') {
        console.log('Map not available, skipping position plotting');
        return;
    }
    
    try {
        // Clear existing markers
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];
        
        if (positions.length === 0) {
            return;
        }
        
        // Create markers for each position
        positions.forEach((pos, index) => {
            const color = getMarkerColor(pos.fix_quality);
            
            const marker = L.circleMarker([pos.lat, pos.lon], {
                radius: 6,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
            
            // Add popup with information
            marker.bindPopup(`
                <strong>Position ${index + 1}</strong><br>
                Lat: ${pos.lat.toFixed(6)}<br>
                Lon: ${pos.lon.toFixed(6)}<br>
                Alt: ${pos.alt.toFixed(1)}m<br>
                Fix: ${pos.fix_quality}<br>
                Satellites: ${pos.num_satellites}<br>
                Time: ${pos.timestamp || 'N/A'}
            `);
            
            markers.push(marker);
        });
        
        // Fit map to show all markers
        if (positions.length > 0) {
            const bounds = L.latLngBounds(positions.map(p => [p.lat, p.lon]));
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    } catch (error) {
        console.error('Error plotting positions:', error);
    }
}

// Get marker color based on fix quality
function getMarkerColor(fixQuality) {
    const colorMap = {
        'RTK Fixed': '#28a745',
        'RTK Float': '#17a2b8',
        'GPS Fix': '#ffc107',
        'DGPS Fix': '#20c997',
        'No Fix': '#dc3545',
        'Estimated': '#fd7e14'
    };
    return colorMap[fixQuality] || '#6c757d';
}

// Update data tables
function updateTables(data) {
    updateGGATable(data.filter(d => d.sentence_type === 'GGA'));
    updateRMCTable(data.filter(d => d.sentence_type === 'RMC'));
    updateGSATable(data.filter(d => d.sentence_type === 'GSA'));
}

// Update GGA table
function updateGGATable(ggaData) {
    const tbody = document.getElementById('gga-tbody');
    tbody.innerHTML = '';
    
    if (ggaData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">No GGA data available</td></tr>';
        return;
    }
    
    ggaData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.timestamp || '-'}</td>
            <td>${row.latitude ? row.latitude.toFixed(6) : '-'}</td>
            <td>${row.longitude ? row.longitude.toFixed(6) : '-'}</td>
            <td>${row.altitude ? row.altitude.toFixed(1) : '-'}</td>
            <td>${row.fix_quality || '-'}</td>
            <td>${row.num_satellites || '-'}</td>
            <td>${row.hdop ? row.hdop.toFixed(1) : '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Update RMC table
function updateRMCTable(rmcData) {
    const tbody = document.getElementById('rmc-tbody');
    tbody.innerHTML = '';
    
    if (rmcData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No RMC data available</td></tr>';
        return;
    }
    
    rmcData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.timestamp || '-'}</td>
            <td>${row.latitude ? row.latitude.toFixed(6) : '-'}</td>
            <td>${row.longitude ? row.longitude.toFixed(6) : '-'}</td>
            <td>${row.speed ? row.speed.toFixed(2) : '-'}</td>
            <td>${row.course ? row.course.toFixed(1) : '-'}</td>
            <td>${row.status || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Update GSA table
function updateGSATable(gsaData) {
    const tbody = document.getElementById('gsa-tbody');
    tbody.innerHTML = '';
    
    if (gsaData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No GSA data available</td></tr>';
        return;
    }
    
    gsaData.forEach(row => {
        const tr = document.createElement('tr');
        const satellites = row.satellite_ids ? row.satellite_ids.join(', ') : '-';
        tr.innerHTML = `
            <td>${row.mode || '-'}</td>
            <td>${row.fix_type || '-'}</td>
            <td>${row.pdop ? row.pdop.toFixed(1) : '-'}</td>
            <td>${row.hdop ? row.hdop.toFixed(1) : '-'}</td>
            <td>${row.vdop ? row.vdop.toFixed(1) : '-'}</td>
            <td>${satellites}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Table toggle buttons
    document.getElementById('toggle-gga').addEventListener('click', function() {
        showTable('gga');
        setActiveButton(this);
    });
    
    document.getElementById('toggle-rmc').addEventListener('click', function() {
        showTable('rmc');
        setActiveButton(this);
    });
    
    document.getElementById('toggle-gsa').addEventListener('click', function() {
        showTable('gsa');
        setActiveButton(this);
    });
    
    // File upload
    document.getElementById('upload-btn').addEventListener('click', handleFileUpload);
}

// Show specific table
function showTable(tableType) {
    document.getElementById('gga-table-container').style.display = 'none';
    document.getElementById('rmc-table-container').style.display = 'none';
    document.getElementById('gsa-table-container').style.display = 'none';
    
    document.getElementById(`${tableType}-table-container`).style.display = 'block';
}

// Set active button
function setActiveButton(button) {
    document.querySelectorAll('.table-controls .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    button.classList.add('active');
}

// Handle file upload
async function handleFileUpload() {
    const fileInput = document.getElementById('file-input');
    const statusDiv = document.getElementById('upload-status');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showStatus('Please select a file first', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showStatus('Uploading and parsing file...', 'success');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showStatus(`Successfully parsed ${result.count} GNSS sentences!`, 'success');
            currentData = result.data;
            updateTables(currentData);
            updateStatistics(result.stats);
            
            // Update map with new positions
            const positions = result.data
                .filter(d => d.sentence_type === 'GGA' && d.latitude && d.longitude)
                .map(d => ({
                    lat: d.latitude,
                    lon: d.longitude,
                    alt: d.altitude || 0,
                    fix_quality: d.fix_quality || 'Unknown',
                    num_satellites: d.num_satellites || 0,
                    timestamp: d.timestamp || ''
                }));
            plotPositions(positions);
        } else {
            showStatus(`Error: ${result.message}`, 'error');
        }
    } catch (error) {
        showStatus(`Error uploading file: ${error.message}`, 'error');
    }
}

// Show status message
function showStatus(message, type) {
    const statusDiv = document.getElementById('upload-status');
    statusDiv.textContent = message;
    statusDiv.className = type;
    statusDiv.style.display = 'block';
}
