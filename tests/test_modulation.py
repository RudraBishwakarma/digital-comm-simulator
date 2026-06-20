"""
Unit tests for modulation functions
"""

import unittest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modulation import modulate, demodulate, get_constellation

class TestModulation(unittest.TestCase):
    
    def test_bpsk(self):
        """Test BPSK modulation/demodulation"""
        bits = np.array([0, 1, 0, 1, 0, 1])
        symbols = modulate(bits, 'BPSK')
        expected = np.array([-1, 1, -1, 1, -1, 1])
        np.testing.assert_array_equal(symbols, expected)
        
        # Demodulate
        rx_bits = demodulate(symbols, 'BPSK')
        np.testing.assert_array_equal(bits, rx_bits)
    
    def test_qpsk(self):
        """Test QPSK modulation/demodulation"""
        bits = np.array([0, 0, 0, 1, 1, 1, 1, 0])
        symbols = modulate(bits, 'QPSK')
        rx_bits = demodulate(symbols, 'QPSK')
        np.testing.assert_array_equal(bits, rx_bits)
    
    def test_16qam(self):
        """Test 16QAM modulation/demodulation"""
        bits = np.random.randint(0, 2, 1000)
        symbols = modulate(bits, '16QAM')
        rx_bits = demodulate(symbols, '16QAM')
        np.testing.assert_array_equal(bits, rx_bits)
    
    def test_constellation(self):
        """Test constellation generation"""
        const = get_constellation('QPSK')
        self.assertEqual(len(const), 4)
        self.assertTrue(np.all(np.abs(const) > 0))

if __name__ == '__main__':
    unittest.main()