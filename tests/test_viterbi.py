"""
Unit tests for Viterbi decoder
"""

import unittest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.viterbi import ConvolutionalCodec

class TestViterbi(unittest.TestCase):
    
    def setUp(self):
        self.codec = ConvolutionalCodec(rate=1/2, constraint_length=3)
    
    def test_encode(self):
        """Test convolutional encoding"""
        data = np.array([1, 0, 1, 0])
        encoded = self.codec.encode(data)
        self.assertEqual(len(encoded), (len(data) + 2) * 2)  # + tail bits
    
    def test_decode_no_errors(self):
        """Test decoding with no errors"""
        data = np.random.randint(0, 2, 100)
        encoded = self.codec.encode(data)
        decoded = self.codec.decode(encoded)
        np.testing.assert_array_equal(data, decoded[:len(data)])
    
    def test_decode_with_errors(self):
        """Test decoding with errors"""
        data = np.random.randint(0, 2, 100)
        encoded = self.codec.encode(data)
        
        # Add 5% errors
        noisy = encoded.copy()
        num_errors = int(len(encoded) * 0.05)
        error_positions = np.random.choice(len(encoded), num_errors, replace=False)
        noisy[error_positions] = 1 - noisy[error_positions]
        
        decoded = self.codec.decode(noisy)
        errors = np.sum(data != decoded[:len(data)])
        self.assertLess(errors, 10)  # Should correct most errors
    
    def test_coding_gain(self):
        """Test coding gain calculation"""
        gain = self.codec.get_encoding_gain()
        self.assertGreaterEqual(gain, 2.0)
        self.assertLessEqual(gain, 6.0)

if __name__ == '__main__':
    unittest.main()