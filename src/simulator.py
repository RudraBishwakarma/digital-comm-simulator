import math
import numpy as np
from tqdm import tqdm
from src.modulation import modulate, demodulate
from src.channel import awgn, multipath_fading
from src.constants import MODULATION_TYPES

class CommSimulator:
    def __init__(self, mod_type='QPSK', sps=8, use_multipath=False):
        self.mod_type = mod_type
        self.sps = sps
        self.use_multipath = use_multipath
        self.bits_per_symbol = MODULATION_TYPES[mod_type]['bits_per_symbol']
        
    def run_ber_simulation(self, num_bits=50000, snr_range=np.arange(0, 15, 2), num_trials=5):
        """Run complete BER simulation"""
        ber_results = []
        theoretical_ber = []
        
        for snr_db in tqdm(snr_range, desc=f"Simulating {self.mod_type}"):
            total_errors = 0
            total_bits = 0
            
            for _ in range(num_trials):
                # Generate data
                data_bits = np.random.randint(0, 2, num_bits)
                
                # Modulate
                tx_symbols = modulate(data_bits, self.mod_type)
                
                # Channel (snr_db is Eb/N0, so convert to Es/N0)
                es_no_db = snr_db + 10 * math.log10(self.bits_per_symbol)
                rx_symbols = awgn(tx_symbols, es_no_db)
                if self.use_multipath:
                    rx_symbols = multipath_fading(rx_symbols)
                
                # Demodulate
                rx_bits = demodulate(rx_symbols, self.mod_type)
                
                # Calculate errors
                min_len = min(len(data_bits), len(rx_bits))
                errors = np.sum(data_bits[:min_len] != rx_bits[:min_len])
                total_errors += errors
                total_bits += min_len
            
            ber = total_errors / total_bits if total_bits > 0 else 1.0
            ber_results.append(ber)
            
            # Theoretical BER approximation
            if self.mod_type == 'BPSK' or self.mod_type == 'QPSK':
                the_ber = 0.5 * math.erfc(np.sqrt(10**(snr_db/10)))
            else:
                the_ber = 0.5 * math.erfc(np.sqrt(10**(snr_db/10) / (self.bits_per_symbol)))
            theoretical_ber.append(the_ber)
        
        return np.array(snr_range), np.array(ber_results), np.array(theoretical_ber)