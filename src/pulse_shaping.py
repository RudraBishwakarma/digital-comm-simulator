import numpy as np
from scipy import signal

def rrc_filter(symbols, sps=8, beta=0.35, filter_length=64):
    """
    Root Raised Cosine pulse shaping
    sps: samples per symbol
    beta: roll-off factor
    """
    # Time vector
    t = np.arange(-filter_length/2, filter_length/2 + 0.1) / sps
    
    # RRC impulse response
    h = np.zeros_like(t, dtype=float)
    for i, t_val in enumerate(t):
        if t_val == 0:
            h[i] = 1 - beta + 4*beta/np.pi
        elif abs(t_val) == 1/(4*beta + 1e-10):  # Avoid division by zero
            h[i] = (beta/np.sqrt(2)) * ((1+2/np.pi)*np.sin(np.pi/(4*beta+1e-10)) + (1-2/np.pi)*np.cos(np.pi/(4*beta+1e-10)))
        else:
            numerator = np.sin(np.pi*t_val*(1-beta)) + 4*beta*t_val*np.cos(np.pi*t_val*(1+beta))
            denominator = np.pi*t_val*(1-(4*beta*t_val)**2)
            h[i] = numerator / denominator if abs(denominator) > 1e-10 else 0
    
    h = h / np.sqrt(sps)  # Normalize
    
    # Upsample
    upsampled = np.zeros(len(symbols) * sps, dtype=complex)
    upsampled[::sps] = symbols
    
    # Filter
    shaped = np.convolve(upsampled, h, mode='full')
    
    return shaped, h

def matched_filter(rx_signal, h, sps=8):
    """Matched filtering (receiver)"""
    # Convolve with time-reversed filter
    filtered = np.convolve(rx_signal, h[::-1], mode='full')
    
    # Downsample
    start = len(h) // 2
    symbols = filtered[start::sps]
    
    return symbols