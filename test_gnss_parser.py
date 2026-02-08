"""
Unit tests for GNSS Parser
"""

import unittest
import os
from gnss_parser import GNSSParser


class TestGNSSParser(unittest.TestCase):
    """Test cases for GNSS data parsing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = GNSSParser()
        self.sample_data_path = os.path.join(
            os.path.dirname(__file__), 
            'sample_data', 
            'sample_gnss.nmea'
        )
    
    def test_parse_gga_sentence(self):
        """Test parsing a GGA sentence"""
        sentence = "$GPGGA,123519,3723.2475,N,12158.3416,W,4,13,0.9,9.0,M,0.0,M,0.8,0000*42"
        result = self.parser.parse_nmea_sentence(sentence)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['sentence_type'], 'GGA')
        self.assertAlmostEqual(result['latitude'], 37.387458, places=5)
        self.assertAlmostEqual(result['longitude'], -121.972360, places=5)
        self.assertEqual(result['fix_quality'], 'RTK Fixed')
        self.assertEqual(result['num_satellites'], 13)
    
    def test_parse_rmc_sentence(self):
        """Test parsing an RMC sentence"""
        sentence = "$GPRMC,123519,A,3723.2475,N,12158.3416,W,0.13,309.62,120598,,,A*6A"
        result = self.parser.parse_nmea_sentence(sentence)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['sentence_type'], 'RMC')
        self.assertEqual(result['status'], 'Active')
    
    def test_parse_gsa_sentence(self):
        """Test parsing a GSA sentence"""
        sentence = "$GPGSA,A,3,10,07,05,02,29,04,08,13,,,,,1.7,0.9,1.5*3D"
        result = self.parser.parse_nmea_sentence(sentence)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['sentence_type'], 'GSA')
        self.assertEqual(result['fix_type'], '3D Fix')
        self.assertAlmostEqual(result['hdop'], 0.9)
    
    def test_parse_invalid_sentence(self):
        """Test parsing an invalid sentence"""
        sentence = "INVALID_SENTENCE"
        result = self.parser.parse_nmea_sentence(sentence)
        self.assertIsNone(result)
    
    def test_parse_file(self):
        """Test parsing a complete NMEA file"""
        if os.path.exists(self.sample_data_path):
            data = self.parser.parse_file(self.sample_data_path)
            self.assertGreater(len(data), 0)
            
            # Check that we got some GGA data
            gga_data = [d for d in data if d.get('sentence_type') == 'GGA']
            self.assertGreater(len(gga_data), 0)
    
    def test_get_summary_statistics(self):
        """Test summary statistics calculation"""
        if os.path.exists(self.sample_data_path):
            data = self.parser.parse_file(self.sample_data_path)
            stats = self.parser.get_summary_statistics(data)
            
            self.assertIn('total_sentences', stats)
            self.assertGreater(stats['total_sentences'], 0)
    
    def test_fix_quality_names(self):
        """Test fix quality name mapping"""
        self.assertEqual(self.parser._get_fix_quality_name(0), 'No Fix')
        self.assertEqual(self.parser._get_fix_quality_name(1), 'GPS Fix')
        self.assertEqual(self.parser._get_fix_quality_name(4), 'RTK Fixed')
        self.assertEqual(self.parser._get_fix_quality_name(5), 'RTK Float')
    
    def test_fix_type_names(self):
        """Test fix type name mapping"""
        self.assertEqual(self.parser._get_fix_type_name('1'), 'No Fix')
        self.assertEqual(self.parser._get_fix_type_name('2'), '2D Fix')
        self.assertEqual(self.parser._get_fix_type_name('3'), '3D Fix')


if __name__ == '__main__':
    unittest.main()
