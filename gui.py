import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import time

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.simulator import CommSimulator
from src.viterbi import ConvolutionalCodec
from src.ofdm import OFDMSimulator
from src.modulation import get_constellation
from src.channel import link_budget

# Page configuration
st.set_page_config(
    page_title="📡 Communication Link Simulator",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #28a745;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #17a2b8;
    }
    </style>
""", unsafe_allow_html=True)

def plot_ber_curve(snr_range, ber_sim, ber_theory, mod_type, title_suffix=""):
    """Plot BER comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.semilogy(snr_range, ber_sim, 'bo-', linewidth=2, markersize=8, label='Simulated')
    ax.semilogy(snr_range, ber_theory, 'r--', linewidth=2, label='Theoretical')
    
    ax.grid(True, which='both', alpha=0.3)
    ax.set_xlabel('Eb/N0 (dB)', fontsize=12)
    ax.set_ylabel('Bit Error Rate (BER)', fontsize=12)
    ax.set_title(f'{mod_type} Performance {title_suffix}', fontsize=14)
    ax.legend(fontsize=11)
    ax.set_ylim([1e-6, 1])
    ax.set_xlim([min(snr_range)-1, max(snr_range)+1])
    
    return fig

def plot_constellation(mod_type):
    """Plot constellation diagram"""
    const = get_constellation(mod_type)
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(np.real(const), np.imag(const), s=100, c='red', alpha=0.7)
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('In-phase (I)')
    ax.set_ylabel('Quadrature (Q)')
    ax.set_title(f'{mod_type} Constellation')
    ax.axis('equal')
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.2)
    ax.axvline(x=0, color='k', linestyle='-', alpha=0.2)
    
    return fig

def run_viterbi_simulation(mod_type, snr_range, num_bits, num_trials):
    """Run Viterbi simulation with error correction"""
    codec = ConvolutionalCodec(rate=1/2, constraint_length=3)
    
    ber_sim = []
    ber_theory = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, snr_db in enumerate(snr_range):
        status_text.text(f"Processing SNR = {snr_db} dB...")
        
        total_errors = 0
        total_bits = 0
        
        for _ in range(num_trials):
            # Generate data
            data_bits = np.random.randint(0, 2, num_bits)
            
            # Encode
            encoded_bits = codec.encode(data_bits)
            
            # Modulate
            from src.modulation import modulate
            tx_symbols = modulate(encoded_bits, mod_type)
            
            # Channel
            from src.channel import awgn
            rx_symbols = awgn(tx_symbols, snr_db)
            
            # Demodulate
            from src.modulation import demodulate
            rx_bits = demodulate(rx_symbols, mod_type)
            
            # Decode
            decoded_bits = codec.decode(rx_bits)
            
            # Calculate BER
            min_len = min(len(data_bits), len(decoded_bits))
            errors = np.sum(data_bits[:min_len] != decoded_bits[:min_len])
            total_errors += errors
            total_bits += min_len
        
        ber = total_errors / total_bits if total_bits > 0 else 1.0
        ber_sim.append(ber)
        
        # Theoretical (with coding gain)
        from src.simulator import CommSimulator
        temp_sim = CommSimulator(mod_type=mod_type)
        _, _, theory = temp_sim.run_ber_simulation(
            num_bits=min(num_bits, 10000),
            snr_range=[snr_db],
            num_trials=min(num_trials, 3)
        )
        # Apply coding gain
        coding_gain = codec.get_encoding_gain()
        ber_theory.append(theory[0] * 10**(-coding_gain/10))
        
        progress_bar.progress((idx + 1) / len(snr_range))
    
    status_text.text("✅ Simulation complete!")
    return np.array(snr_range), np.array(ber_sim), np.array(ber_theory), codec

def run_ofdm_simulation(mod_type, snr_range, num_bits, num_trials, num_subcarriers, cp_length):
    """Run OFDM simulation"""
    ofdm_sim = OFDMSimulator(
        mod_type=mod_type,
        num_subcarriers=num_subcarriers,
        cp_length=cp_length
    )
    
    ber_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, snr_db in enumerate(snr_range):
        status_text.text(f"Processing SNR = {snr_db} dB...")
        
        total_ber = 0
        for _ in range(num_trials):
            ber = ofdm_sim.ber_simulation(
                num_bits=min(num_bits, 10000),
                snr_db=snr_db
            )
            total_ber += ber
        
        ber_results.append(total_ber / num_trials)
        progress_bar.progress((idx + 1) / len(snr_range))
    
    status_text.text("✅ Simulation complete!")
    
    # Calculate theoretical for comparison
    from src.simulator import CommSimulator
    temp_sim = CommSimulator(mod_type=mod_type)
    _, _, theory = temp_sim.run_ber_simulation(
        num_bits=min(num_bits, 10000),
        snr_range=snr_range,
        num_trials=min(num_trials, 3)
    )
    
    return np.array(snr_range), np.array(ber_results), theory, ofdm_sim

def main():
    """Main GUI application"""
    
    # Header
    st.markdown('<p class="main-header">📡 Digital Communication Link Simulator</p>', 
                unsafe_allow_html=True)
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # System selection
        system_type = st.selectbox(
            "System Type",
            ["Basic AWGN", "With Viterbi Coding", "OFDM System"],
            help="Choose which system to simulate"
        )
        
        # Modulation
        mod_type = st.selectbox(
            "Modulation Scheme",
            ["BPSK", "QPSK", "16QAM", "64QAM"]
        )
        
        st.divider()
        
        # SNR range
        st.subheader("📊 SNR Settings")
        col1, col2 = st.columns(2)
        with col1:
            snr_min = st.number_input("Min SNR (dB)", 0, 10, 0)
        with col2:
            snr_max = st.number_input("Max SNR (dB)", 10, 30, 20)
        snr_step = st.slider("SNR Step (dB)", 1, 5, 2)
        
        snr_range = np.arange(snr_min, snr_max + 1, snr_step)
        
        st.divider()
        
        # Simulation parameters
        st.subheader("⚡ Simulation Parameters")
        num_bits = st.number_input("Bits per trial", 1000, 100000, 30000, step=1000)
        num_trials = st.number_input("Trials per SNR", 1, 20, 5, step=1)
        
        st.divider()
        
        # Channel options
        st.subheader("📡 Channel Settings")
        use_multipath = st.checkbox("Enable Multipath Fading", value=False)
        
        st.divider()
        
        # Viterbi options
        if system_type == "With Viterbi Coding":
            st.subheader("🔧 Viterbi Settings")
            code_rate = st.selectbox("Code Rate", ["1/2", "1/3"], index=0)
            constraint_length = st.slider("Constraint Length", 3, 7, 3, step=2)
            
            st.info(f"💡 Coding gain: ~{3 + (constraint_length-3)//2} dB")
        
        # OFDM options
        if system_type == "OFDM System":
            st.subheader("📶 OFDM Settings")
            num_subcarriers = st.selectbox("Number of Subcarriers", [32, 64, 128], index=1)
            cp_length = st.slider("Cyclic Prefix Length", 8, 32, 16)
        
        st.divider()
        
        # Run button
        run_button = st.button("🚀 Run Simulation", use_container_width=True, type="primary")
    
    # Main content area
    if run_button:
        with st.spinner("🔄 Running simulation... Please wait."):
            
            # Display parameters
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("System", system_type)
            with col2:
                st.metric("Modulation", mod_type)
            with col3:
                st.metric("SNR Range", f"{snr_min} - {snr_max} dB")
            with col4:
                st.metric("Trials", num_trials)
            
            # Run appropriate simulation
            if system_type == "Basic AWGN":
                # Create simulator
                sim = CommSimulator(
                    mod_type=mod_type,
                    sps=8,
                    use_multipath=use_multipath
                )
                
                # Run simulation
                snr, ber_sim, ber_theory = sim.run_ber_simulation(
                    num_bits=num_bits,
                    snr_range=snr_range,
                    num_trials=num_trials
                )
                
                # Display results
                st.subheader("📊 BER Performance")
                
                # Plot BER curve
                fig = plot_ber_curve(snr, ber_sim, ber_theory, mod_type)
                st.pyplot(fig)
                
                # Show metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    best_ber = ber_sim[-1] if len(ber_sim) > 0 else 1.0
                    st.metric("Best BER", f"{best_ber:.2e}")
                with col2:
                    if np.any(ber_sim < 1e-3):
                        idx = np.where(ber_sim < 1e-3)[0][0]
                        st.metric("SNR @ BER=1e-3", f"{snr[idx]:.1f} dB")
                    else:
                        st.metric("SNR @ BER=1e-3", "N/A")
                with col3:
                    match = "✅" if np.mean(np.abs(ber_sim - ber_theory)) < 0.1 else "⚠️"
                    st.metric("Theoretical Match", match)
                
                # Show constellation
                st.subheader("🌟 Constellation Diagram")
                fig2 = plot_constellation(mod_type)
                st.pyplot(fig2)
            
            elif system_type == "With Viterbi Coding":
                # Run Viterbi simulation
                snr, ber_sim, ber_theory, codec = run_viterbi_simulation(
                    mod_type, snr_range, num_bits, num_trials
                )
                
                # Display results
                st.subheader("📊 BER Performance with Viterbi Coding")
                
                # Plot BER curve
                fig = plot_ber_curve(snr, ber_sim, ber_theory, mod_type, "(with Viterbi)")
                st.pyplot(fig)
                
                # Show coding info
                info = codec.get_info()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Code Rate", f"{info['rate']:.1f}")
                with col2:
                    st.metric("Constraint Length", info['constraint_length'])
                with col3:
                    st.metric("Polynomials", info['polynomials'])
                with col4:
                    st.metric("Coding Gain", f"{info['coding_gain']:.1f} dB")
                
                # Show constellation
                st.subheader("🌟 Constellation Diagram")
                fig2 = plot_constellation(mod_type)
                st.pyplot(fig2)
                
                st.success(f"✅ Viterbi coding active with {info['coding_gain']:.1f} dB coding gain!")
            
            elif system_type == "OFDM System":
                # Run OFDM simulation
                snr, ber_sim, ber_theory, ofdm_sim = run_ofdm_simulation(
                    mod_type, snr_range, num_bits, num_trials, 
                    num_subcarriers, cp_length
                )
                
                # Display results
                st.subheader("📊 BER Performance with OFDM")
                
                # Plot BER curve
                fig = plot_ber_curve(snr, ber_sim, ber_theory, mod_type, "(OFDM)")
                st.pyplot(fig)
                
                # Show OFDM info
                info = ofdm_sim.get_info()
                ofdm_config = info['ofdm_config']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Subcarriers", ofdm_config['num_subcarriers'])
                with col2:
                    st.metric("CP Length", ofdm_config['cp_length'])
                with col3:
                    st.metric("Pilots", ofdm_config['num_pilots'])
                with col4:
                    st.metric("Data Carriers", ofdm_config['data_subcarriers'])
                
                # Show constellation
                st.subheader("🌟 Constellation Diagram")
                fig2 = plot_constellation(mod_type)
                st.pyplot(fig2)
                
                # Visualize OFDM signal
                if st.button("📶 Visualize OFDM Signal"):
                    data = np.random.randint(0, 2, 1000)
                    tx_signal = ofdm_sim.transmit(data)
                    
                    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
                    
                    # Time domain
                    ax[0].plot(np.real(tx_signal[:200]), 'b-', alpha=0.7)
                    ax[0].set_title('OFDM Signal (Time Domain - Real Part)')
                    ax[0].grid(True, alpha=0.3)
                    ax[0].set_xlabel('Sample')
                    ax[0].set_ylabel('Amplitude')
                    
                    # Frequency domain
                    freq_signal = np.fft.fft(tx_signal)
                    ax[1].plot(np.abs(freq_signal[:len(freq_signal)//2]), 'r-', alpha=0.7)
                    ax[1].set_title('OFDM Signal (Frequency Domain - Magnitude)')
                    ax[1].grid(True, alpha=0.3)
                    ax[1].set_xlabel('Frequency Bin')
                    ax[1].set_ylabel('Magnitude')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                
                st.success(f"✅ OFDM System: {num_subcarriers} subcarriers, CP={cp_length}")
            
            # Link Budget Analysis (always show)
            st.divider()
            st.subheader("📡 Link Budget Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                freq = st.number_input("Frequency (GHz)", 0.5, 100.0, 2.4, step=0.1)
                distance = st.number_input("Distance (km)", 0.1, 100.0, 1.0, step=0.1)
            
            with col2:
                tx_power = st.number_input("Transmit Power (dBm)", 0, 30, 10)
                tx_gain = st.number_input("TX Antenna Gain (dB)", 0, 30, 2)
                rx_gain = st.number_input("RX Antenna Gain (dB)", 0, 30, 2)
            
            if st.button("📊 Calculate Link Budget"):
                rx_power, path_loss = link_budget(
                    freq=freq*1e9,
                    distance=distance*1000,
                    tx_power=tx_power,
                    tx_gain=tx_gain,
                    rx_gain=rx_gain
                )
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Path Loss", f"{path_loss:.1f} dB")
                with col2:
                    st.metric("Received Power", f"{rx_power:.1f} dBm")
                with col3:
                    margin = rx_power + 90
                    if margin > 0:
                        st.metric("Link Margin", f"{margin:.1f} dB", delta="✅ Good")
                    else:
                        st.metric("Link Margin", f"{margin:.1f} dB", delta="⚠️ Low")
    
    else:
        # Show welcome screen
        st.info("👈 Configure your simulation in the sidebar and click **'Run Simulation'**")
        
        # Show features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📊 Basic AWGN
            - Standard BER simulation
            - Multiple modulations
            - Matches theory
            - Fast execution
            """)
        
        with col2:
            st.markdown("""
            ### 🔧 Viterbi Coding
            - Error correction
            - 3-5 dB coding gain
            - Improved BER
            - Uses commpy
            """)
        
        with col3:
            st.markdown("""
            ### 📡 OFDM System
            - Multi-carrier modulation
            - Robust to multipath
            - 4G/5G compatible
            - Pilot-based channel estimation
            """)
        
        # Show sample constellation
        st.subheader("🌟 Sample Constellation (QPSK)")
        fig = plot_constellation('QPSK')
        st.pyplot(fig)

if __name__ == "__main__":
    main()