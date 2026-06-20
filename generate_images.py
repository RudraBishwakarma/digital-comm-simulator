"""
Generate all images for README
Run: python generate_images.py
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.patches as patches

# Create images folder if it doesn't exist
os.makedirs('images', exist_ok=True)

def generate_ber_curves():
    """Generate BER curves for all modulations"""
    print("📊 Generating BER curves...")
    
    from src.simulator import CommSimulator
    
    modulations = ['BPSK', 'QPSK', '16QAM']
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for idx, mod_type in enumerate(modulations):
        ax = axes[idx]
        
        sim = CommSimulator(mod_type=mod_type)
        
        # Adjust bits for each modulation
        bits_per_symbol = {'BPSK': 1, 'QPSK': 2, '16QAM': 4, '64QAM': 6}
        num_bits = 24000  # Multiple of all: 1, 2, 4, 6 (LCM = 12, so 24000 works)
        
        snr, ber_sim, ber_theory = sim.run_ber_simulation(
            num_bits=num_bits,
            snr_range=np.arange(0, 16, 2),
            num_trials=3
        )
        
        ax.semilogy(snr, ber_sim, 'bo-', linewidth=2, markersize=8, label='Simulated')
        ax.semilogy(snr, ber_theory, 'r--', linewidth=2, label='Theoretical')
        ax.grid(True, which='both', alpha=0.3)
        ax.set_xlabel('Eb/N0 (dB)')
        ax.set_ylabel('Bit Error Rate (BER)')
        ax.set_title(f'{mod_type} Performance')
        ax.legend()
        ax.set_ylim([1e-6, 1])
    
    # Hide the 4th subplot (empty)
    axes[3].axis('off')
    
    plt.tight_layout()
    plt.savefig('images/ber_curves_all.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Saved: images/ber_curves_all.png")
    
    # Also save individual QPSK curve (for main README)
    sim = CommSimulator(mod_type='QPSK')
    snr, ber_sim, ber_theory = sim.run_ber_simulation(
        num_bits=30000,
        snr_range=np.arange(0, 16, 2),
        num_trials=5
    )
    
    plt.figure(figsize=(10, 6))
    plt.semilogy(snr, ber_sim, 'bo-', linewidth=2, markersize=8, label='Simulated QPSK')
    plt.semilogy(snr, ber_theory, 'r--', linewidth=2, label='Theoretical QPSK')
    plt.grid(True, which='both', alpha=0.3)
    plt.xlabel('Eb/N0 (dB)')
    plt.ylabel('Bit Error Rate (BER)')
    plt.title('QPSK Performance in AWGN Channel')
    plt.legend()
    plt.ylim([1e-6, 1])
    plt.savefig('images/ber_curve.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Saved: images/ber_curve.png")

def generate_constellations():
    """Generate constellation diagrams"""
    print("\n🌟 Generating constellation diagrams...")
    
    from src.modulation import get_constellation
    
    modulations = ['BPSK', 'QPSK', '16QAM', '64QAM']
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for idx, mod_type in enumerate(modulations):
        ax = axes[idx]
        const = get_constellation(mod_type)
        ax.scatter(np.real(const), np.imag(const), s=100, c='red', alpha=0.7)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('In-phase (I)')
        ax.set_ylabel('Quadrature (Q)')
        ax.set_title(f'{mod_type} Constellation')
        ax.axis('equal')
        ax.axhline(y=0, color='k', linestyle='-', alpha=0.2)
        ax.axvline(x=0, color='k', linestyle='-', alpha=0.2)
    
    plt.tight_layout()
    plt.savefig('images/constellation_all.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Saved: images/constellation_all.png")
    
    # Also save individual QPSK
    const = get_constellation('QPSK')
    plt.figure(figsize=(6, 6))
    plt.scatter(np.real(const), np.imag(const), s=100, c='red', alpha=0.7)
    plt.grid(True, alpha=0.3)
    plt.xlabel('In-phase (I)')
    plt.ylabel('Quadrature (Q)')
    plt.title('QPSK Constellation')
    plt.axis('equal')
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    plt.axvline(x=0, color='k', linestyle='-', alpha=0.2)
    plt.savefig('images/constellation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Saved: images/constellation.png")

def generate_system_diagram():
    """Generate system block diagram"""
    print("\n📡 Generating system diagram...")
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 4))
    
    blocks = [
        ('Data\nBits', 0.08, 0.5),
        ('Convolutional\nEncoder', 0.23, 0.5),
        ('Modulator\n(BPSK/QPSK/\n16QAM/64QAM)', 0.38, 0.5),
        ('Channel\n(AWGN/\nMultipath)', 0.58, 0.5),
        ('Demodulator\n& Equalizer', 0.78, 0.5),
        ('Viterbi\nDecoder', 0.93, 0.5),
    ]
    
    colors = ['#E8F4F8', '#D4EDDA', '#FFF3CD', '#F8D7DA', '#D1ECF1', '#E8D5F5']
    
    for (name, x, y), color in zip(blocks, colors):
        rect = patches.FancyBboxPatch(
            (x-0.07, y-0.2), 0.14, 0.4,
            boxstyle='round,pad=0.02',
            facecolor=color,
            edgecolor='#333',
            linewidth=2
        )
        ax.add_patch(rect)
        ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Arrows
    positions = [0.15, 0.30, 0.48, 0.68, 0.85]
    for x in positions:
        ax.annotate('', xy=(x+0.05, 0.5), xytext=(x, 0.5),
                    arrowprops=dict(arrowstyle='->', lw=2, color='#333'))
    
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Digital Communication System Block Diagram', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('images/system_diagram.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Saved: images/system_diagram.png")

def generate_link_budget():
    """Generate link budget visualization"""
    print("\n📊 Generating link budget visualization...")
    
    from src.channel import link_budget
    
    distances = np.linspace(0.1, 10, 50)  # km
    rx_powers = []
    
    for d in distances:
        rx_power, _ = link_budget(freq=2.4e9, distance=d*1000, tx_power=20)
        rx_powers.append(rx_power)
    
    plt.figure(figsize=(10, 6))
    plt.plot(distances, rx_powers, 'b-', linewidth=2)
    plt.grid(True, alpha=0.3)
    plt.xlabel('Distance (km)')
    plt.ylabel('Received Power (dBm)')
    plt.title('Link Budget: Received Power vs Distance (2.4 GHz, 20 dBm TX)')
    plt.axhline(y=-90, color='r', linestyle='--', label='Sensitivity Limit')
    plt.legend()
    plt.savefig('images/link_budget.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Saved: images/link_budget.png")

def main():
    print("=" * 60)
    print("📸 GENERATING IMAGES FOR README")
    print("=" * 60)
    
    generate_ber_curves()
    generate_constellations()
    generate_system_diagram()
    generate_link_budget()
    
    print("\n" + "=" * 60)
    print("✅ All images generated in 'images/' folder!")
    print("=" * 60)
    
    # List all images
    if os.path.exists('images'):
        print("\n📁 Images created:")
        for f in os.listdir('images'):
            if f.endswith('.png'):
                size = os.path.getsize(f'images/{f}') / 1024
                print(f"  📷 {f} ({size:.1f} KB)")

if __name__ == "__main__":
    main()