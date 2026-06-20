"""
Main simulation runner using centralized configuration
"""

import numpy as np
import matplotlib.pyplot as plt
from src.simulator import CommSimulator
from src.channel import link_budget
from src.config import (
    SIMULATION,
    get_snr_range,
    get_modulation_info,
    LINK_BUDGET,
    print_config
)

def main():
    print("=" * 60)
    print("🚀 DIGITAL COMMUNICATION SIMULATOR")
    print("=" * 60)
    
    # Print configuration
    print_config()
    
    # Configuration - Using centralized values
    MODULATION = 'QPSK'  # Change to 'BPSK', '16QAM', '64QAM'
    SNR_RANGE = get_snr_range()
    NUM_BITS = SIMULATION['num_bits']
    NUM_TRIALS = SIMULATION['num_trials']
    
    print(f"\n📡 Running Simulation for {MODULATION}")
    print(f"   SNR Range: {SNR_RANGE[0]} to {SNR_RANGE[-1]} dB")
    print(f"   Bits per trial: {NUM_BITS}")
    print(f"   Trials per SNR: {NUM_TRIALS}")
    print("\n🔄 Running simulation...")
    
    # Create simulator
    sim = CommSimulator(
        mod_type=MODULATION,
        sps=SIMULATION['sps'],
        use_multipath=SIMULATION['use_multipath']
    )
    
    # Run simulation
    snr, ber_sim, ber_theory = sim.run_ber_simulation(
        num_bits=NUM_BITS,
        snr_range=SNR_RANGE,
        num_trials=NUM_TRIALS
    )
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.semilogy(snr, ber_sim, 'bo-', linewidth=2, markersize=8, label=f'Simulated {MODULATION}')
    plt.semilogy(snr, ber_theory, 'r--', linewidth=2, label=f'Theoretical {MODULATION}')
    plt.grid(True, which='both', alpha=0.3)
    plt.xlabel('Eb/N0 (dB)', fontsize=12)
    plt.ylabel('Bit Error Rate (BER)', fontsize=12)
    plt.title(f'{MODULATION} Performance in AWGN Channel', fontsize=14)
    plt.legend(fontsize=11)
    plt.ylim([1e-6, 1])
    plt.tight_layout()
    plt.savefig(f'ber_{MODULATION}.png', dpi=150)
    plt.show()
    
    print(f"\n✅ Simulation complete! Results saved to ber_{MODULATION}.png")
    
    # Link budget
    rx_power, path_loss = link_budget(
        freq=LINK_BUDGET['frequency'],
        distance=LINK_BUDGET['distance'],
        tx_power=LINK_BUDGET['tx_power'],
        tx_gain=LINK_BUDGET['tx_gain'],
        rx_gain=LINK_BUDGET['rx_gain']
    )
    
    print(f"\n📡 Link Budget Analysis:")
    print(f"   Frequency: {LINK_BUDGET['frequency']/1e9:.1f} GHz")
    print(f"   Distance: {LINK_BUDGET['distance']/1000:.1f} km")
    print(f"   TX Power: {LINK_BUDGET['tx_power']} dBm")
    print(f"   Path Loss: {path_loss:.1f} dB")
    print(f"   Received Power: {rx_power:.1f} dBm")
    print(f"   Link Margin: {rx_power - LINK_BUDGET['sensitivity']:.1f} dB")

if __name__ == "__main__":
    main()