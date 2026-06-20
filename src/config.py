"""
Central Configuration File for Digital Communication Simulator
All parameters are defined here for easy modification
"""

import numpy as np

# ============================================
# 1. MODULATION PARAMETERS
# ============================================
MODULATION_TYPES = {
    'BPSK': {
        'order': 2,
        'bits_per_symbol': 1,
        'constellation': [-1, 1],
        'normalization': 1.0,
        'snr_for_ber_1e3': 6.8,  # SNR (dB) for BER = 1e-3
        'snr_for_ber_1e5': 9.6,  # SNR (dB) for BER = 1e-5
        'color': 'blue'
    },
    'QPSK': {
        'order': 4,
        'bits_per_symbol': 2,
        'constellation': [1+1j, -1+1j, -1-1j, 1-1j],
        'normalization': np.sqrt(2),
        'snr_for_ber_1e3': 6.8,
        'snr_for_ber_1e5': 9.6,
        'color': 'green'
    },
    '16QAM': {
        'order': 16,
        'bits_per_symbol': 4,
        'constellation': '16QAM',  # Generated dynamically
        'normalization': np.sqrt(10),
        'snr_for_ber_1e3': 12.5,
        'snr_for_ber_1e5': 15.3,
        'color': 'red'
    },
    '64QAM': {
        'order': 64,
        'bits_per_symbol': 6,
        'constellation': '64QAM',  # Generated dynamically
        'normalization': np.sqrt(42),
        'snr_for_ber_1e3': 18.2,
        'snr_for_ber_1e5': 21.0,
        'color': 'purple'
    }
}

# ============================================
# 2. SIMULATION PARAMETERS
# ============================================
SIMULATION = {
    'snr_min': 0,           # Minimum SNR (dB)
    'snr_max': 14,          # Maximum SNR (dB)
    'snr_step': 2,          # SNR step size
    'num_bits': 30000,      # Bits per trial (MUST be multiple of all modulations bits/symbol)
    'num_trials': 5,        # Number of trials per SNR point
    'sps': 8,               # Samples per symbol (for pulse shaping)
    'use_multipath': False, # Default: False (AWGN only)
}

# ============================================
# 3. PULSE SHAPING PARAMETERS
# ============================================
PULSE_SHAPING = {
    'rrc_beta': 0.35,       # Roll-off factor (0.1 to 1.0)
    'filter_length': 64,    # Filter length in samples
    'sps': 8,               # Samples per symbol
}

# ============================================
# 4. FRAME STRUCTURE
# ============================================
FRAME = {
    'symbols_per_frame': 1000,  # Number of symbols per frame
    'preamble_length': 64,      # Preamble length in bits (for synchronization)
}

# ============================================
# 5. CHANNEL PARAMETERS
# ============================================
CHANNEL = {
    'multipath_taps': [1.0, 0.5, 0.25],  # Amplitude of each path
    'multipath_delays': [0, 2, 4],       # Delay in samples
    'rayleigh_scale': np.sqrt(0.5),      # Rayleigh fading scale
}

# ============================================
# 6. LINK BUDGET PARAMETERS
# ============================================
LINK_BUDGET = {
    'frequency': 2.4e9,     # 2.4 GHz (WiFi)
    'distance': 1000,       # 1 km
    'tx_power': 10,         # 10 dBm
    'tx_gain': 2,           # 2 dBi
    'rx_gain': 2,           # 2 dBi
    'sensitivity': -90,     # Receiver sensitivity (dBm)
    'speed_of_light': 3e8,  # m/s
}

# ============================================
# 7. VITERBI PARAMETERS
# ============================================
VITERBI = {
    'default_rate': 1/2,    # Code rate (1/2 or 1/3)
    'default_constraint': 3, # Constraint length (3, 5, 7)
    'polynomials': {
        3: [0o7, 0o5],      # [7, 5] for constraint 3
        5: [0o35, 0o23],    # [35, 23] for constraint 5
        7: [0o171, 0o133],  # [171, 133] for constraint 7
    },
    'coding_gain': {
        3: 3.0,             # ~3 dB for constraint 3
        5: 4.0,             # ~4 dB for constraint 5
        7: 5.0,             # ~5 dB for constraint 7
    }
}

# ============================================
# 8. OFDM PARAMETERS
# ============================================
OFDM = {
    'default_subcarriers': 64,  # FFT size (32, 64, 128)
    'default_cp_length': 16,    # Cyclic prefix length
    'default_pilots': 8,        # Number of pilot subcarriers
    'data_subcarriers': 55,     # Computed: subcarriers - pilots - 1 (DC)
    'pilot_values': 1 + 1j,     # Pilot value (normalized)
}

# ============================================
# 9. GUI PARAMETERS
# ============================================
GUI = {
    'page_title': '📡 Communication Link Simulator',
    'page_icon': '📡',
    'layout': 'wide',
    'available_modulations': ['BPSK', 'QPSK', '16QAM', '64QAM'],
    'system_types': ['Basic AWGN', 'With Viterbi Coding', 'OFDM System'],
    'code_rates': ['1/2', '1/3'],
    'constraint_lengths': [3, 5, 7],
    'subcarrier_options': [32, 64, 128],
    'cp_length_options': [8, 12, 16, 20, 24, 28, 32],
}

# ============================================
# 10. TESTING PARAMETERS
# ============================================
TESTING = {
    'test_bits': 100,       # Bits for quick tests
    'performance_bits': 1000, # Bits for performance tests
    'full_bits': 30000,     # Bits for full simulation
    'tolerance': 0.1,       # Tolerance for test assertions
}

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_snr_range():
    """Get SNR range from config"""
    return np.arange(
        SIMULATION['snr_min'],
        SIMULATION['snr_max'] + SIMULATION['snr_step'],
        SIMULATION['snr_step']
    )

def get_modulation_info(mod_type):
    """Get modulation parameters for a specific type"""
    return MODULATION_TYPES.get(mod_type, MODULATION_TYPES['QPSK'])

def get_viterbi_gain(constraint_length):
    """Get coding gain for a specific constraint length"""
    return VITERBI['coding_gain'].get(constraint_length, 3.0)

def get_link_budget_info():
    """Get link budget parameters"""
    return LINK_BUDGET

def print_config():
    """Print all configuration values"""
    print("=" * 60)
    print("📊 COMMUNICATION SIMULATOR - CONFIGURATION")
    print("=" * 60)
    
    print("\n1️⃣ MODULATION PARAMETERS:")
    for mod, params in MODULATION_TYPES.items():
        print(f"   {mod}: {params['bits_per_symbol']} bits/symbol, SNR@1e-3: {params['snr_for_ber_1e3']} dB")
    
    print(f"\n2️⃣ SIMULATION PARAMETERS:")
    print(f"   SNR Range: {SIMULATION['snr_min']} to {SIMULATION['snr_max']} dB, step {SIMULATION['snr_step']}")
    print(f"   Bits per trial: {SIMULATION['num_bits']}")
    print(f"   Trials per SNR: {SIMULATION['num_trials']}")
    print(f"   Samples per symbol: {SIMULATION['sps']}")
    
    print(f"\n3️⃣ VITERBI PARAMETERS:")
    print(f"   Default Rate: {VITERBI['default_rate']}")
    print(f"   Default Constraint: {VITERBI['default_constraint']}")
    print(f"   Coding Gain: {VITERBI['coding_gain'][VITERBI['default_constraint']]} dB")
    
    print(f"\n4️⃣ OFDM PARAMETERS:")
    print(f"   Subcarriers: {OFDM['default_subcarriers']}")
    print(f"   Cyclic Prefix: {OFDM['default_cp_length']}")
    print(f"   Pilots: {OFDM['default_pilots']}")
    
    print(f"\n5️⃣ LINK BUDGET:")
    print(f"   Frequency: {LINK_BUDGET['frequency']/1e9:.1f} GHz")
    print(f"   Distance: {LINK_BUDGET['distance']/1000:.1f} km")
    print(f"   TX Power: {LINK_BUDGET['tx_power']} dBm")
    print("=" * 60)

if __name__ == "__main__":
    print_config()