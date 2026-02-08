"""
GNSS Data Parser
Parses NMEA sentences and extracts positioning information
"""

import pynmea2
from datetime import datetime
from typing import List, Dict, Optional


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
        
        stats = {
            'total_sentences': len(data),
            'gga_count': len(gga_data),
            'gsa_count': len(gsa_data),
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
            
            if alts:
                stats['avg_altitude'] = sum(alts) / len(alts)
            
            if sats:
                stats['avg_satellites'] = sum(sats) / len(sats)
            
            # Count fix types
            fix_types = {}
            for d in gga_data:
                fix_type = d.get('fix_quality', 'Unknown')
                fix_types[fix_type] = fix_types.get(fix_type, 0) + 1
            stats['fix_types'] = fix_types
        
        if gsa_data:
            hdops = [d['hdop'] for d in gsa_data if d.get('hdop') and d['hdop'] > 0]
            if hdops:
                stats['avg_hdop'] = sum(hdops) / len(hdops)
        
        return stats
