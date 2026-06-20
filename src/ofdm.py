import numpy as np

class OFDMModulator:
    """Complete OFDM modulator/demodulator"""
    
    def __init__(self, num_subcarriers=64, cp_length=16, num_pilots=8):
        """
        num_subcarriers: Number of subcarriers (FFT size)
        cp_length: Cyclic prefix length
        num_pilots: Number of pilot subcarriers
        """
        self.num_subcarriers = num_subcarriers
        self.cp_length = cp_length
        self.num_pilots = num_pilots
        
        # Pilot positions (scattered throughout)
        self.pilot_positions = np.arange(1, num_subcarriers-1, 
                                         num_subcarriers//num_pilots)[:num_pilots]
        
        # Pilot values (known by receiver)
        self.pilot_values = np.ones(num_pilots) * (1 + 1j) / np.sqrt(2)
        
        # Get data positions (all positions except pilots and DC)
        self.data_positions = [i for i in range(1, self.num_subcarriers-1) 
                               if i not in self.pilot_positions]
        
        # Data subcarriers count (actual, not calculated)
        self.data_subcarriers = len(self.data_positions)
    
    def modulate(self, symbols):
        """
        Convert symbols to OFDM signal
        symbols: Input symbols (length = data_subcarriers)
        """
        # Pad or truncate symbols to fit in data subcarriers
        if len(symbols) > self.data_subcarriers:
            symbols = symbols[:self.data_subcarriers]
        elif len(symbols) < self.data_subcarriers:
            # Zero-pad
            symbols = np.concatenate([symbols, np.zeros(self.data_subcarriers - len(symbols))])
        
        # Create frequency domain frame
        freq_domain = np.zeros(self.num_subcarriers, dtype=complex)
        
        # Place data symbols
        freq_domain[self.data_positions] = symbols
        
        # Insert pilots
        freq_domain[self.pilot_positions] = self.pilot_values
        
        # IFFT to time domain
        time_domain = np.fft.ifft(freq_domain)
        
        # Add cyclic prefix
        cp = time_domain[-self.cp_length:]
        ofdm_symbol = np.concatenate([cp, time_domain])
        
        return ofdm_symbol, freq_domain
    
    def demodulate(self, rx_signal):
        """
        Demodulate OFDM signal back to symbols
        rx_signal: Received time-domain signal
        """
        # Remove cyclic prefix
        if len(rx_signal) >= self.num_subcarriers + self.cp_length:
            rx_signal = rx_signal[self.cp_length:self.cp_length + self.num_subcarriers]
        else:
            # Pad if too short
            rx_signal = np.pad(rx_signal, (0, self.num_subcarriers + self.cp_length - len(rx_signal)))
            rx_signal = rx_signal[self.cp_length:self.cp_length + self.num_subcarriers]
        
        # FFT to frequency domain
        freq_domain = np.fft.fft(rx_signal)
        
        # Extract pilots
        rx_pilots = freq_domain[self.pilot_positions]
        
        # Channel estimation (interpolate between pilots)
        channel_estimate = self.estimate_channel(rx_pilots)
        
        # Equalize data subcarriers
        equalized = freq_domain[self.data_positions] / (channel_estimate[self.data_positions] + 1e-10)
        
        # Extract valid symbols (remove zero padding)
        valid_symbols = equalized[np.abs(equalized) > 1e-6]
        
        return valid_symbols, channel_estimate
    
    def estimate_channel(self, rx_pilots):
        """Estimate channel response from received pilots"""
        # Least squares estimate at pilot positions
        h_pilot = rx_pilots / (self.pilot_values + 1e-10)
        
        # Simple interpolation to all subcarriers
        channel_estimate = np.ones(self.num_subcarriers, dtype=complex)
        
        # Linear interpolation between pilots
        for i in range(len(self.pilot_positions)-1):
            start = self.pilot_positions[i]
            end = self.pilot_positions[i+1]
            h_start = h_pilot[i]
            h_end = h_pilot[i+1]
            
            for j in range(start, end+1):
                alpha = (j - start) / (end - start + 1)
                channel_estimate[j] = h_start * (1-alpha) + h_end * alpha
        
        return channel_estimate
    
    def get_info(self):
        """Get OFDM configuration info"""
        return {
            'num_subcarriers': self.num_subcarriers,
            'cp_length': self.cp_length,
            'num_pilots': self.num_pilots,
            'data_subcarriers': self.data_subcarriers,
            'pilot_positions': self.pilot_positions.tolist()
        }


class OFDMSimulator:
    """Complete OFDM system with modulation"""
    
    def __init__(self, mod_type='QPSK', num_subcarriers=64, cp_length=16):
        self.mod_type = mod_type
        self.ofdm = OFDMModulator(num_subcarriers, cp_length)
        self.num_subcarriers = num_subcarriers
        self.cp_length = cp_length
        
        # Import modulation
        try:
            from src.modulation import modulate, demodulate
            self.modulate_fn = modulate
            self.demodulate_fn = demodulate
        except ImportError:
            # Fallback for testing
            self.modulate_fn = None
            self.demodulate_fn = None
    
    def _get_modulate(self):
        """Lazy load modulation functions"""
        if self.modulate_fn is None:
            try:
                from src.modulation import modulate, demodulate
                self.modulate_fn = modulate
                self.demodulate_fn = demodulate
            except ImportError:
                # Simple fallback for testing
                def simple_modulate(bits, mod_type='QPSK'):
                    if mod_type == 'BPSK':
                        return 2 * bits - 1
                    elif mod_type == 'QPSK':
                        bits = bits.reshape(-1, 2)
                        symbols = np.zeros(len(bits), dtype=complex)
                        for i, (b0, b1) in enumerate(bits):
                            real = 1 if b0 == 0 else -1
                            imag = 1 if b1 == 0 else -1
                            symbols[i] = real + 1j*imag
                        return symbols / np.sqrt(2)
                    else:
                        return 2 * bits - 1
                
                def simple_demodulate(symbols, mod_type='QPSK'):
                    if mod_type == 'BPSK':
                        return (np.real(symbols) > 0).astype(int)
                    elif mod_type == 'QPSK':
                        bits = []
                        for sym in symbols:
                            real_bit = 0 if np.real(sym) > 0 else 1
                            imag_bit = 0 if np.imag(sym) > 0 else 1
                            bits.extend([real_bit, imag_bit])
                        return np.array(bits)
                    else:
                        return (np.real(symbols) > 0).astype(int)
                
                self.modulate_fn = simple_modulate
                self.demodulate_fn = simple_demodulate
        return self.modulate_fn, self.demodulate_fn
    
    def transmit(self, data_bits):
        """Complete OFDM transmitter"""
        mod_fn, _ = self._get_modulate()
        
        # Modulate bits to symbols
        symbols = mod_fn(data_bits, self.mod_type)
        
        # OFDM modulation
        ofdm_signal, _ = self.ofdm.modulate(symbols)
        
        return ofdm_signal
    
    def receive(self, rx_signal):
        """Complete OFDM receiver"""
        _, demod_fn = self._get_modulate()
        
        # OFDM demodulation
        symbols, channel_est = self.ofdm.demodulate(rx_signal)
        
        # Demodulate symbols to bits
        rx_bits = demod_fn(symbols, self.mod_type)
        
        return rx_bits, channel_est
    
    def ber_simulation(self, num_bits=10000, snr_db=10):
        """Run BER simulation for OFDM"""
        # Generate data
        data_bits = np.random.randint(0, 2, num_bits)
        
        # Transmit
        tx_signal = self.transmit(data_bits)
        
        # Channel (AWGN)
        try:
            from src.channel import awgn
            rx_signal = awgn(tx_signal, snr_db)
        except ImportError:
            # Simple AWGN
            signal_power = np.mean(np.abs(tx_signal)**2)
            snr_linear = 10**(snr_db/10)
            noise_power = signal_power / snr_linear
            noise = np.sqrt(noise_power/2) * (np.random.randn(*tx_signal.shape) + 1j*np.random.randn(*tx_signal.shape))
            rx_signal = tx_signal + noise
        
        # Receive
        rx_bits, _ = self.receive(rx_signal)
        
        # Calculate BER
        min_len = min(len(data_bits), len(rx_bits))
        ber = np.sum(data_bits[:min_len] != rx_bits[:min_len]) / min_len if min_len > 0 else 1.0
        
        return ber
    
    def get_info(self):
        """Get system info"""
        return {
            'mod_type': self.mod_type,
            'ofdm_config': self.ofdm.get_info()
        }


def test_ofdm():
    """Test OFDM system"""
    print("\n" + "=" * 50)
    print("TESTING OFDM SYSTEM")
    print("=" * 50)
    
    # Test different configurations
    configs = [
        (64, 16, "QPSK"),
        (64, 16, "BPSK"),
    ]
    
    results = []
    
    for num_subcarriers, cp_length, mod_type in configs:
        print(f"\nTesting OFDM: {num_subcarriers} subcarriers, CP={cp_length}, {mod_type}")
        
        try:
            ofdm = OFDMSimulator(
                mod_type=mod_type,
                num_subcarriers=num_subcarriers,
                cp_length=cp_length
            )
            
            # Test with data
            data = np.random.randint(0, 2, 100)
            tx_signal = ofdm.transmit(data)
            
            print(f"  Data bits: {len(data)}")
            print(f"  OFDM signal length: {len(tx_signal)} samples")
            
            # Test receive (no noise)
            rx_bits, channel = ofdm.receive(tx_signal)
            
            # Calculate BER
            min_len = min(len(data), len(rx_bits))
            if min_len > 0:
                errors = np.sum(data[:min_len] != rx_bits[:min_len])
                ber = errors / min_len
                print(f"  Errors after receive: {errors}")
                print(f"  BER = {ber:.4f}")
                
                if ber == 0:
                    print("  ✅ OFDM test PASSED")
                    results.append(True)
                else:
                    print("  ⚠️ OFDM test has errors (may be expected)")
                    results.append(False)
            else:
                print("  ❌ No bits recovered")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ OFDM test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"OFDM TESTS: {sum(results)}/{len(results)} PASSED")
    print("=" * 50)
    
    return all(results)


if __name__ == "__main__":
    test_ofdm()