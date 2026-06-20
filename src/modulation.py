import numpy as np

def modulate(bits, mod_type='BPSK'):
    """Map bits to complex symbols"""
    if mod_type == 'BPSK':
        return 2 * bits - 1  # 0->-1, 1->1
    
    elif mod_type == 'QPSK':
        bits = bits.reshape(-1, 2)
        symbols = np.zeros(len(bits), dtype=complex)
        for i, (b0, b1) in enumerate(bits):
            # Gray mapping: 00->1+j, 01->-1+j, 11->-1-j, 10->1-j
            real = 1 if b0 == 0 else -1
            imag = 1 if b1 == 0 else -1
            symbols[i] = real + 1j*imag
        return symbols / np.sqrt(2)  # Normalize to unit power
    
    elif mod_type == '16QAM':
        bits = bits.reshape(-1, 4)
        symbols = np.zeros(len(bits), dtype=complex)
        
        # Define the exact mapping: bits -> (real, imag) values
        # Bit pairs: (b0,b1) -> real value, (b2,b3) -> imag value
        # Using Gray coding: 00->-3, 01->-1, 11->1, 10->3
        mapping = {
            (0, 0): -3,
            (0, 1): -1,
            (1, 1): 1,
            (1, 0): 3
        }
        
        for i, b in enumerate(bits):
            real = mapping[(b[0], b[1])]
            imag = mapping[(b[2], b[3])]
            symbols[i] = real + 1j*imag
        return symbols / np.sqrt(10)  # Normalize to unit power
    
    elif mod_type == '64QAM':
        bits = bits.reshape(-1, 6)
        symbols = np.zeros(len(bits), dtype=complex)
        for i, b in enumerate(bits):
            const = np.array([-7, -5, -3, -1, 1, 3, 5, 7])
            idx_real = b[0]*4 + b[1]*2 + b[2]
            idx_imag = b[3]*4 + b[4]*2 + b[5]
            symbols[i] = const[idx_real] + 1j*const[idx_imag]
        return symbols / np.sqrt(42)  # Normalize to unit power

def demodulate(symbols, mod_type='BPSK'):
    """Demodulate symbols to bits (hard decision)"""
    if mod_type == 'BPSK':
        return (np.real(symbols) > 0).astype(int)
    
    elif mod_type == 'QPSK':
        bits = []
        for sym in symbols:
            real_bit = 0 if np.real(sym) > 0 else 1
            imag_bit = 0 if np.imag(sym) > 0 else 1
            bits.extend([real_bit, imag_bit])
        return np.array(bits)
    
    elif mod_type == '16QAM':
        # Denormalize first (multiply by sqrt(10))
        symbols = symbols * np.sqrt(10)
        
        bits = []
        const = np.array([-3, -1, 1, 3])
        
        # EXACT reverse mapping of the modulate function
        # Values: -3 -> bits (0,0), -1 -> bits (0,1), 1 -> bits (1,1), 3 -> bits (1,0)
        value_to_bits = {
            -3: [0, 0],
            -1: [0, 1],
            1: [1, 1],
            3: [1, 0]
        }
        
        for sym in symbols:
            # Find nearest constellation point
            real_idx = np.argmin(np.abs(np.real(sym) - const))
            imag_idx = np.argmin(np.abs(np.imag(sym) - const))
            
            # Get the actual values
            real_val = const[real_idx]
            imag_val = const[imag_idx]
            
            # Convert to bits using the mapping
            bits.extend(value_to_bits[real_val] + value_to_bits[imag_val])
        return np.array(bits)
    
    elif mod_type == '64QAM':
        # Denormalize first (multiply by sqrt(42))
        symbols = symbols * np.sqrt(42)
        
        bits = []
        const = np.array([-7, -5, -3, -1, 1, 3, 5, 7])
        for sym in symbols:
            real_idx = np.argmin(np.abs(np.real(sym) - const))
            imag_idx = np.argmin(np.abs(np.imag(sym) - const))
            real_bits = [(real_idx >> 2) & 1, (real_idx >> 1) & 1, real_idx & 1]
            imag_bits = [(imag_idx >> 2) & 1, (imag_idx >> 1) & 1, imag_idx & 1]
            bits.extend(real_bits + imag_bits)
        return np.array(bits)

def get_constellation(mod_type):
    """Generate constellation points for plotting"""
    if mod_type == 'BPSK':
        return np.array([-1, 1])
    elif mod_type == 'QPSK':
        return np.array([1+1j, -1+1j, -1-1j, 1-1j]) / np.sqrt(2)
    elif mod_type == '16QAM':
        const = np.array([-3, -1, 1, 3])
        points = []
        for r in const:
            for i in const:
                points.append(r + 1j*i)
        return np.array(points) / np.sqrt(10)
    elif mod_type == '64QAM':
        const = np.array([-7, -5, -3, -1, 1, 3, 5, 7])
        points = []
        for r in const:
            for i in const:
                points.append(r + 1j*i)
        return np.array(points) / np.sqrt(42)