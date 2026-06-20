"""
Digital Communication Simulator
A complete physical-layer communication system simulator
"""

from src.simulator import CommSimulator
from src.viterbi import ConvolutionalCodec
from src.ofdm import OFDMSimulator
from src.modulation import modulate, demodulate, get_constellation
from src.channel import awgn, multipath_fading, link_budget

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    'CommSimulator',
    'ConvolutionalCodec',
    'OFDMSimulator',
    'modulate',
    'demodulate',
    'get_constellation',
    'awgn',
    'multipath_fading',
    'link_budget'
]