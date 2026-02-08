"""
GNSS Data Parser
Parses NMEA sentences and extracts positioning information
Includes position correction algorithms for enhanced accuracy
"""

import pynmea2
from datetime import datetime
from typing import List, Dict, Optional
import statistics
import math


class GNSSParser:
    """Parser for GNSS NMEA sentences"""
    
    def __init__(self):
        self.data = []
    
    def parse_nmea_sentence(self, sentence: str) -> Optional[Dict]:
        """Parse a single NMEA sentence and return structured data"""
        try:
            msg = pynmea2.parse(sentence)
            
            # Parse GGA sentences (GPS Fix Data)
            if isinstance(msg, pynmea2.types.talker.GGA):
                return {
                    'timestamp': msg.timestamp.isoformat() if msg.timestamp else None,
                    'latitude': msg.latitude if msg.latitude else 0.0,
                    'longitude': msg.longitude if msg.longitude else 0.0,
                    'altitude': float(msg.altitude) if msg.altitude else 0.0,
                    'fix_quality': self._get_fix_quality_name(msg.gps_qual),
                    'num_satellites': int(msg.num_sats) if msg.num_sats else 0,
                    'hdop': float(msg.horizontal_dil) if msg.horizontal_dil else 0.0,
                    'sentence_type': 'GGA'
                }
            
            # Parse RMC sentences (Recommended Minimum)
            elif isinstance(msg, pynmea2.types.talker.RMC):
                return {
                    'timestamp': msg.timestamp.isoformat() if msg.timestamp else None,
                    'latitude': msg.latitude if msg.latitude else 0.0,
                    'longitude': msg.longitude if msg.longitude else 0.0,
                    'speed': float(msg.spd_over_grnd) if msg.spd_over_grnd else 0.0,
                    'course': float(msg.true_course) if msg.true_course else 0.0,
                    'status': 'Active' if msg.status == 'A' else 'Void',
                    'sentence_type': 'RMC'
                }
            
            # Parse GSA sentences (DOP and active satellites)
            elif isinstance(msg, pynmea2.types.talker.GSA):
                return {
                    'mode': msg.mode,
                    'fix_type': self._get_fix_type_name(msg.mode_fix_type),
                    'pdop': float(msg.pdop) if msg.pdop else 0.0,
                    'hdop': float(msg.hdop) if msg.hdop else 0.0,
                    'vdop': float(msg.vdop) if msg.vdop else 0.0,
                    'satellite_ids': [s for s in [msg.sv_id01, msg.sv_id02, msg.sv_id03, msg.sv_id04,
                                                   msg.sv_id05, msg.sv_id06, msg.sv_id07, msg.sv_id08,
                                                   msg.sv_id09, msg.sv_id10, msg.sv_id11, msg.sv_id12] if s],
                    'sentence_type': 'GSA'
                }
            
            # Parse GSV sentences (Satellites in view)
            elif isinstance(msg, pynmea2.types.talker.GSV):
                satellites = []
                for i in range(1, 5):  # GSV can have up to 4 satellites per sentence
                    sat_id = getattr(msg, f'sv_prn_num_{i}', None)
                    if sat_id:
                        satellites.append({
                            'id': sat_id,
                            'elevation': getattr(msg, f'elevation_deg_{i}', None),
                            'azimuth': getattr(msg, f'azimuth_{i}', None),
                            'snr': getattr(msg, f'snr_{i}', None)
                        })
                
                return {
                    'num_messages': int(msg.num_messages) if msg.num_messages else 1,
                    'msg_num': int(msg.msg_num) if msg.msg_num else 1,
                    'num_sv_in_view': int(msg.num_sv_in_view) if msg.num_sv_in_view else 0,
                    'satellites': satellites,
                    'sentence_type': 'GSV'
                }
                
        except pynmea2.ParseError as e:
            return None
        except Exception as e:
            return None
        
        return None
    
    def _get_fix_quality_name(self, quality: int) -> str:
        """Convert GPS quality indicator to human-readable name"""
        quality_map = {
            0: 'No Fix',
            1: 'GPS Fix',
            2: 'DGPS Fix',
            3: 'PPS Fix',
            4: 'RTK Fixed',
            5: 'RTK Float',
            6: 'Estimated',
            7: 'Manual',
            8: 'Simulation'
        }
        return quality_map.get(int(quality), 'Unknown')
    
    def _get_fix_type_name(self, fix_type: str) -> str:
        """Convert fix type to human-readable name"""
        fix_map = {
            '1': 'No Fix',
            '2': '2D Fix',
            '3': '3D Fix'
        }
        return fix_map.get(str(fix_type), 'Unknown')
    
    def parse_file(self, filepath: str) -> List[Dict]:
        """Parse an entire NMEA log file"""
        parsed_data = []
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('$'):
                        result = self.parse_nmea_sentence(line)
                        if result:
                            parsed_data.append(result)
        except Exception as e:
            print(f"Error parsing file: {e}")
        
        return parsed_data
    
    def get_summary_statistics(self, data: List[Dict]) -> Dict:
        """Calculate summary statistics from parsed GNSS data"""
        if not data:
            return {}
        
        gga_data = [d for d in data if d.get('sentence_type') == 'GGA']
        gsa_data = [d for d in data if d.get('sentence_type') == 'GSA']
        rmc_data = [d for d in data if d.get('sentence_type') == 'RMC']
        
        stats = {
            'total_sentences': len(data),
            'gga_count': len(gga_data),
            'gsa_count': len(gsa_data),
            'rmc_count': len(rmc_data),
        }
        
        if gga_data:
            # Calculate position statistics
            lats = [d['latitude'] for d in gga_data if d.get('latitude')]
            lons = [d['longitude'] for d in gga_data if d.get('longitude')]
            alts = [d['altitude'] for d in gga_data if d.get('altitude')]
            sats = [d['num_satellites'] for d in gga_data if d.get('num_satellites')]
            
            if lats and lons:
                stats['avg_latitude'] = sum(lats) / len(lats)
                stats['avg_longitude'] = sum(lons) / len(lons)
                stats['min_latitude'] = min(lats)
                stats['max_latitude'] = max(lats)
                stats['min_longitude'] = min(lons)
                stats['max_longitude'] = max(lons)
                
                # Calculate position spread (simple distance approximation)
                # Note: Uses simplified Euclidean distance assuming flat Earth.
                # For higher accuracy over longer distances, consider Haversine formula.
                lat_range = max(lats) - min(lats)
                lon_range = max(lons) - min(lons)
                stats['position_spread_meters'] = ((lat_range ** 2 + lon_range ** 2) ** 0.5) * 111000  # Rough conversion to meters
            
            if alts:
                stats['avg_altitude'] = sum(alts) / len(alts)
                stats['min_altitude'] = min(alts)
                stats['max_altitude'] = max(alts)
                stats['altitude_range'] = max(alts) - min(alts)
            
            if sats:
                stats['avg_satellites'] = sum(sats) / len(sats)
                stats['min_satellites'] = min(sats)
                stats['max_satellites'] = max(sats)
            
            # Count fix types
            fix_types = {}
            for d in gga_data:
                fix_type = d.get('fix_quality', 'Unknown')
                fix_types[fix_type] = fix_types.get(fix_type, 0) + 1
            stats['fix_types'] = fix_types
            
            # Calculate fix type percentages
            if fix_types:
                fix_percentages = {}
                for fix_type, count in fix_types.items():
                    fix_percentages[fix_type] = round((count / len(gga_data)) * 100, 1)
                stats['fix_percentages'] = fix_percentages
        
        if gsa_data:
            hdops = [d['hdop'] for d in gsa_data if d.get('hdop') and d['hdop'] > 0]
            pdops = [d['pdop'] for d in gsa_data if d.get('pdop') and d['pdop'] > 0]
            vdops = [d['vdop'] for d in gsa_data if d.get('vdop') and d['vdop'] > 0]
            
            if hdops:
                stats['avg_hdop'] = sum(hdops) / len(hdops)
                stats['min_hdop'] = min(hdops)
                stats['max_hdop'] = max(hdops)
            
            if pdops:
                stats['avg_pdop'] = sum(pdops) / len(pdops)
            
            if vdops:
                stats['avg_vdop'] = sum(vdops) / len(vdops)
        
        # Calculate signal quality assessment
        if gga_data:
            good_fixes = sum(1 for d in gga_data if d.get('fix_quality') in ['RTK Fixed', 'RTK Float', 'DGPS Fix'])
            stats['signal_quality_percent'] = round((good_fixes / len(gga_data)) * 100, 1) if gga_data else 0
        
        return stats
    
    def calculate_position_corrections(self, data: List[Dict], method: str = 'mean', 
                                      weight_by_quality: bool = True) -> Dict:
        """
        Calculate position corrections based on multiple readings
        
        Args:
            data: List of parsed GNSS data
            method: Correction method ('mean', 'median', 'weighted_average')
            weight_by_quality: Whether to weight by fix quality and satellite count
            
        Returns:
            Dictionary with correction data and statistics
        """
        gga_data = [d for d in data if d.get('sentence_type') == 'GGA' and 
                    d.get('latitude') and d.get('longitude')]
        
        if len(gga_data) < 2:
            return {
                'error': 'Insufficient data for corrections (need at least 2 position fixes)',
                'num_points': len(gga_data)
            }
        
        # Extract positions
        lats = [d['latitude'] for d in gga_data]
        lons = [d['longitude'] for d in gga_data]
        alts = [d.get('altitude', 0) for d in gga_data]
        
        # Calculate corrections based on method
        if method == 'mean':
            corrected_lat = statistics.mean(lats)
            corrected_lon = statistics.mean(lons)
            corrected_alt = statistics.mean(alts) if any(alts) else 0
            
        elif method == 'median':
            corrected_lat = statistics.median(lats)
            corrected_lon = statistics.median(lons)
            corrected_alt = statistics.median(alts) if any(alts) else 0
            
        elif method == 'weighted_average':
            # Weight by fix quality and number of satellites
            weights = []
            quality_weights = {
                'RTK Fixed': 10.0,
                'RTK Float': 5.0,
                'DGPS Fix': 2.0,
                'GPS Fix': 1.0,
                'No Fix': 0.1
            }
            
            for d in gga_data:
                quality_weight = quality_weights.get(d.get('fix_quality', 'Unknown'), 1.0)
                # Default to 4 satellites (minimum for 3D positioning) if not available
                sat_weight = d.get('num_satellites', 4) / 12.0  # Normalize to typical good satellite count (12)
                hdop = d.get('hdop', 2.0)
                # Use 0.5 as minimum to prevent division by zero and cap max weight for excellent HDOP
                hdop_weight = 1.0 / max(hdop, 0.5)  # Lower HDOP is better (inverted for weight)
                
                total_weight = quality_weight * sat_weight * hdop_weight if weight_by_quality else 1.0
                weights.append(total_weight)
            
            # Weighted average calculation
            total_weight = sum(weights)
            corrected_lat = sum(lat * w for lat, w in zip(lats, weights)) / total_weight
            corrected_lon = sum(lon * w for lon, w in zip(lons, weights)) / total_weight
            corrected_alt = sum(alt * w for alt, w in zip(alts, weights)) / total_weight if any(alts) else 0
        else:
            return {'error': f'Unknown correction method: {method}'}
        
        # Calculate correction statistics
        lat_corrections = [corrected_lat - lat for lat in lats]
        lon_corrections = [corrected_lon - lon for lon in lons]
        alt_corrections = [corrected_alt - alt for alt in alts]
        
        # Calculate distances in meters (approximate)
        correction_distances = []
        for i in range(len(lats)):
            dlat = (corrected_lat - lats[i]) * 111000  # degrees to meters
            dlon = (corrected_lon - lons[i]) * 111000 * math.cos(math.radians(lats[i]))
            distance = math.sqrt(dlat**2 + dlon**2)
            correction_distances.append(distance)
        
        # Calculate standard deviations before and after
        lat_std_before = statistics.stdev(lats) if len(lats) > 1 else 0
        lon_std_before = statistics.stdev(lons) if len(lons) > 1 else 0
        
        # Position spread before correction
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        spread_before = math.sqrt(lat_range**2 + lon_range**2) * 111000
        
        return {
            'corrected_position': {
                'latitude': corrected_lat,
                'longitude': corrected_lon,
                'altitude': corrected_alt
            },
            'original_center': {
                'latitude': statistics.mean(lats),
                'longitude': statistics.mean(lons),
                'altitude': statistics.mean(alts) if any(alts) else 0
            },
            'corrections': {
                'mean_lat_correction': statistics.mean(lat_corrections),
                'mean_lon_correction': statistics.mean(lon_corrections),
                'mean_alt_correction': statistics.mean(alt_corrections) if any(alts) else 0,
                'mean_distance_correction_m': statistics.mean(correction_distances),
                'max_distance_correction_m': max(correction_distances),
                'min_distance_correction_m': min(correction_distances)
            },
            'accuracy_improvement': {
                'lat_std_before': lat_std_before,
                'lon_std_before': lon_std_before,
                'spread_before_m': spread_before,
                'num_points': len(gga_data)
            },
            'method': method,
            'weight_by_quality': weight_by_quality
        }
    
    def apply_corrections_to_data(self, data: List[Dict], correction_info: Dict) -> List[Dict]:
        """
        Apply calculated corrections to the dataset
        
        Args:
            data: Original parsed GNSS data
            correction_info: Correction information from calculate_position_corrections
            
        Returns:
            New dataset with corrected positions
        """
        if 'error' in correction_info:
            return data
        
        corrected_data = []
        corrected_pos = correction_info['corrected_position']
        
        for d in data:
            new_d = d.copy()
            if d.get('sentence_type') == 'GGA' and d.get('latitude') and d.get('longitude'):
                # For visualization purposes, we keep original but add corrected field
                new_d['latitude_original'] = d['latitude']
                new_d['longitude_original'] = d['longitude']
                new_d['altitude_original'] = d.get('altitude', 0)
                
                # Set to corrected values
                new_d['latitude_corrected'] = corrected_pos['latitude']
                new_d['longitude_corrected'] = corrected_pos['longitude']
                new_d['altitude_corrected'] = corrected_pos['altitude']
                
            corrected_data.append(new_d)
        
        return corrected_data
