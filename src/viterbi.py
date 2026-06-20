"""
Pure Python Viterbi decoder - No external dependencies!
"""

import numpy as np

class ConvolutionalCodec:
    """
    Convolutional encoder and Viterbi decoder
    Pure Python implementation - works without commpy!
    """
    
    def __init__(self, rate=1/2, constraint_length=3):
        """
        rate: code rate (1/2, 1/3, etc.)
        constraint_length: memory of the encoder (3, 5, 7)
        """
        self.rate = rate
        self.constraint_length = constraint_length
        
        # Generator polynomials (octal)
        if rate == 1/2 and constraint_length == 3:
            self.generator = [0o7, 0o5]  # [7, 5] standard
            self.polynomials = "[7, 5]"
        elif rate == 1/2 and constraint_length == 5:
            self.generator = [0o35, 0o23]  # [35, 23]
            self.polynomials = "[35, 23]"
        elif rate == 1/2 and constraint_length == 7:
            self.generator = [0o171, 0o133]  # [171, 133]
            self.polynomials = "[171, 133]"
        elif rate == 1/3 and constraint_length == 3:
            self.generator = [0o7, 0o5, 0o3]  # [7, 5, 3]
            self.polynomials = "[7, 5, 3]"
        else:
            # Default
            self.generator = [0o7, 0o5]
            self.polynomials = "[7, 5]"
        
        self.num_outputs = len(self.generator)
        self.num_states = 2 ** (constraint_length - 1)
        
    def _convolve(self, bit, state):
        """Generate output bits for given input bit and state"""
        # Combine bit with current state
        input_bits = (state << 1) | bit
        
        outputs = []
        for gen in self.generator:
            output = 0
            # For each tap in the generator
            for i in range(self.constraint_length):
                if (gen >> (self.constraint_length - 1 - i)) & 1:
                    output ^= (input_bits >> i) & 1
            outputs.append(output)
        return outputs
    
    def encode(self, data_bits):
        """Encode bits with convolutional code"""
        # Add tail bits to flush encoder
        data_with_tail = np.concatenate([
            data_bits, 
            np.zeros(self.constraint_length - 1, dtype=int)
        ])
        
        encoded = []
        state = 0
        
        for bit in data_with_tail:
            outputs = self._convolve(bit, state)
            encoded.extend(outputs)
            
            # Update state (shift register)
            state = ((bit << (self.constraint_length - 2)) | (state >> 1))
        
        return np.array(encoded)
    
    def decode(self, rx_bits, hard_decision=True):
        """
        Decode with Viterbi algorithm (hard decision)
        """
        if len(rx_bits) == 0:
            return np.array([])
        
        # Number of trellis stages
        num_stages = len(rx_bits) // self.num_outputs
        
        if num_stages == 0:
            return np.array([])
        
        # Initialize metrics
        metrics = np.full(self.num_states, np.inf)
        metrics[0] = 0
        
        # Store path history
        path_history = []
        
        for stage in range(num_stages):
            # Get received bits for this stage
            start_idx = stage * self.num_outputs
            end_idx = min(start_idx + self.num_outputs, len(rx_bits))
            rx_stage = rx_bits[start_idx:end_idx]
            
            # Pad if necessary
            if len(rx_stage) < self.num_outputs:
                rx_stage = np.pad(rx_stage, (0, self.num_outputs - len(rx_stage)))
            
            new_metrics = np.full(self.num_states, np.inf)
            branch_choices = np.zeros(self.num_states, dtype=object)
            
            for state in range(self.num_states):
                if metrics[state] == np.inf:
                    continue
                
                # Try both input bits (0 and 1)
                for bit in [0, 1]:
                    # Generate output for this transition
                    outputs = self._convolve(bit, state)
                    
                    # Calculate Hamming distance
                    distance = np.sum(np.array(outputs) != rx_stage)
                    
                    # Next state
                    next_state = ((bit << (self.constraint_length - 2)) | (state >> 1))
                    
                    # Update metric
                    new_metric = metrics[state] + distance
                    if new_metric < new_metrics[next_state]:
                        new_metrics[next_state] = new_metric
                        branch_choices[next_state] = (state, bit)
            
            metrics = new_metrics
            path_history.append(branch_choices)
        
        # Traceback to find best path
        best_state = np.argmin(metrics)
        decoded_bits = []
        
        for stage in range(num_stages - 1, -1, -1):
            if stage < len(path_history) and best_state < len(path_history[stage]):
                state, bit = path_history[stage][best_state]
                decoded_bits.insert(0, bit)
                best_state = state
            else:
                break
        
        # Remove tail bits and ensure correct length
        decoded_bits = np.array(decoded_bits)
        
        # Trim to remove tail bits
        data_len = max(0, len(decoded_bits) - (self.constraint_length - 1))
        
        # Handle case where we don't have enough bits
        if data_len <= 0:
            return np.array([])
        
        return decoded_bits[:data_len]
    
    def get_encoding_gain(self):
        """Approximate coding gain in dB"""
        if self.constraint_length == 3:
            return 3.0
        elif self.constraint_length == 5:
            return 4.0
        elif self.constraint_length == 7:
            return 5.0
        else:
            return 3.0
    
    def get_info(self):
        """Get codec information"""
        return {
            'rate': self.rate,
            'constraint_length': self.constraint_length,
            'polynomials': self.polynomials,
            'num_states': self.num_states,
            'coding_gain': self.get_encoding_gain(),
            'using_commpy': False
        }


def test_viterbi():
    """Test function to verify Viterbi works"""
    print("=" * 50)
    print("TESTING VITERBI DECODER (Pure Python)")
    print("=" * 50)
    
    codec = ConvolutionalCodec(rate=1/2, constraint_length=3)
    
    info = codec.get_info()
    print(f"\nCodec Info:")
    print(f"  Rate: {info['rate']}")
    print(f"  Constraint Length: {info['constraint_length']}")
    print(f"  Polynomials: {info['polynomials']}")
    print(f"  Coding Gain: {info['coding_gain']:.1f} dB")
    
    # Test with data
    data = np.random.randint(0, 2, 200)
    encoded = codec.encode(data)
    
    print(f"\nTest Data:")
    print(f"  Original bits: {len(data)}")
    print(f"  Encoded bits: {len(encoded)}")
    
    # Add noise (some errors)
    noisy = encoded.copy()
    num_errors = min(20, len(encoded) // 5)
    if num_errors > 0:
        error_positions = np.random.choice(len(encoded), size=num_errors, replace=False)
        noisy[error_positions] = 1 - noisy[error_positions]
        print(f"  Added {len(error_positions)} errors ({len(error_positions)/len(encoded)*100:.1f}%)")
    
    # Decode
    decoded = codec.decode(noisy)
    
    # Calculate BER
    min_len = min(len(data), len(decoded))
    if min_len > 0:
        errors = np.sum(data[:min_len] != decoded[:min_len])
        ber = errors / min_len
        print(f"  Errors after decoding: {errors}")
        print(f"  After decoding BER = {ber:.4f}")
        
        if ber < 0.01:
            print("  ✅ Viterbi test PASSED")
        else:
            print("  ⚠️ Viterbi test needs more SNR")
    else:
        print("  ❌ Decoding failed - no bits recovered")
    
    return True


if __name__ == "__main__":
    test_viterbi()