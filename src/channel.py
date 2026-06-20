import numpy as np

def awgn(signal, snr_db):
    """Add Additive White Gaussian Noise to the signal"""
    signal_power = np.mean(np.abs(signal)**2)
    if signal_power == 0:
        return signal
    snr_linear = 10**(snr_db/10)
    noise_power = signal_power / snr_linear
    noise = np.sqrt(noise_power/2) * (np.random.randn(*signal.shape) + 1j*np.random.randn(*signal.shape))
    return signal + noise

def multipath_fading(signal, taps=[1.0, 0.5, 0.25], delays=[0, 2, 4]):
    """
    Tapped-delay-line multipath fading channel
    taps: amplitude of each path
    delays: delay in samples for each path
    """
    output = np.zeros(len(signal) + max(delays), dtype=complex)
    for tap, delay in zip(taps, delays):
        # Rayleigh fading for each tap
        fading = np.sqrt(0.5) * (np.random.randn(len(signal)) + 1j*np.random.randn(len(signal)))
        output[delay:delay+len(signal)] += tap * signal * fading
    return output[:len(signal)]

def link_budget(freq=2.4e9, distance=1000, tx_power=10, tx_gain=2, rx_gain=2):
    """
    Calculate theoretical link budget
    Returns: received power (dBm), path loss (dB)
    """
    c = 3e8  # Speed of light
    wavelength = c / freq
    
    # Free Space Path Loss
    fspl = 20*np.log10(4*np.pi*distance/wavelength)
    
    # Received power
    rx_power = tx_power + tx_gain + rx_gain - fspl
    
    return rx_power, fspl