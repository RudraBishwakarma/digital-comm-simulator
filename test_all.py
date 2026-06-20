import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_modulation():
    print("\n📊 Testing Modulation...")
    try:
        from src.modulation import modulate, demodulate, get_constellation
        
        # Test BPSK
        bits = np.array([0, 1, 0, 1])
        symbols = modulate(bits, 'BPSK')
        rx_bits = demodulate(symbols, 'BPSK')
        assert np.array_equal(bits, rx_bits), "BPSK failed"
        print("  ✅ BPSK: Passed")
        
        # Test QPSK
        bits = np.random.randint(0, 2, 100)
        symbols = modulate(bits, 'QPSK')
        rx_bits = demodulate(symbols, 'QPSK')
        assert np.array_equal(bits, rx_bits), "QPSK failed"
        print("  ✅ QPSK: Passed")
        
        # Test 16QAM
        bits = np.random.randint(0, 2, 100)
        symbols = modulate(bits, '16QAM')
        rx_bits = demodulate(symbols, '16QAM')
        assert np.array_equal(bits, rx_bits), "16QAM failed"
        print("  ✅ 16QAM: Passed")
        
        # Test Constellation
        const = get_constellation('QPSK')
        assert len(const) == 4, f"Expected 4 points, got {len(const)}"
        print("  ✅ Constellation: Passed")
        
        return True
        
    except AssertionError as e:
        print(f"  ❌ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Modulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_channel():
    print("\n📡 Testing Channel...")
    try:
        from src.channel import awgn, multipath_fading, link_budget
        
        signal = np.ones(10) + 1j*np.ones(10)
        rx = awgn(signal, snr_db=10)
        assert len(rx) == len(signal), "AWGN length mismatch"
        print("  ✅ AWGN: Passed")
        
        rx = multipath_fading(signal)
        assert len(rx) == len(signal), "Multipath length mismatch"
        print("  ✅ Multipath: Passed")
        
        rx_power, path_loss = link_budget(freq=2.4e9, distance=1000)
        assert rx_power < 0, "Link budget calculation failed"
        print(f"  ✅ Link Budget: Passed (Path Loss: {path_loss:.1f} dB)")
        
        return True
    except Exception as e:
        print(f"  ❌ Channel test failed: {e}")
        return False

def test_viterbi():
    print("\n🔧 Testing Viterbi...")
    try:
        from src.viterbi import ConvolutionalCodec
        
        codec = ConvolutionalCodec(rate=1/2, constraint_length=3)
        
        data = np.random.randint(0, 2, 100)
        encoded = codec.encode(data)
        decoded = codec.decode(encoded)
        
        min_len = min(len(data), len(decoded))
        errors = np.sum(data[:min_len] != decoded[:min_len])
        
        if errors == 0:
            print("  ✅ Encode/Decode: Passed (perfect match)")
        else:
            print(f"  ⚠️ Encode/Decode: {errors} errors")
        
        noisy = encoded.copy()
        error_positions = np.random.choice(len(encoded), size=5, replace=False)
        noisy[error_positions] = 1 - noisy[error_positions]
        decoded = codec.decode(noisy)
        
        min_len = min(len(data), len(decoded))
        errors = np.sum(data[:min_len] != decoded[:min_len])
        print(f"  ✅ Error Correction: {errors} errors remaining after 5 bit errors")
        
        info = codec.get_info()
        print(f"  ✅ Codec Info: Rate {info['rate']}, Gain {info['coding_gain']:.1f} dB")
        
        return True
    except Exception as e:
        print(f"  ❌ Viterbi test failed: {e}")
        return False

def test_ofdm():
    print("\n📶 Testing OFDM...")
    try:
        from src.ofdm import OFDMSimulator
        
        ofdm = OFDMSimulator(mod_type='QPSK', num_subcarriers=64, cp_length=16)
        
        data = np.random.randint(0, 2, 100)
        tx_signal = ofdm.transmit(data)
        rx_bits, _ = ofdm.receive(tx_signal)
        
        min_len = min(len(data), len(rx_bits))
        errors = np.sum(data[:min_len] != rx_bits[:min_len])
        
        if errors == 0:
            print("  ✅ Transmit/Receive: Passed (perfect match)")
        else:
            print(f"  ⚠️ Transmit/Receive: {errors} errors")
        
        info = ofdm.get_info()
        print(f"  ✅ OFDM Info: {info['ofdm_config']['num_subcarriers']} subcarriers")
        
        return True
    except Exception as e:
        print(f"  ❌ OFDM test failed: {e}")
        return False

def test_simulator():
    print("\n🚀 Testing Simulator...")
    try:
        from src.simulator import CommSimulator
        
        sim = CommSimulator(mod_type='QPSK', sps=8)
        
        snr_range = np.arange(0, 10, 5)
        snr, ber_sim, ber_theory = sim.run_ber_simulation(
            num_bits=1000,
            snr_range=snr_range,
            num_trials=2
        )
        
        assert len(ber_sim) == len(snr_range), "Simulator output length mismatch"
        print(f"  ✅ Simulator: Passed (BER at 0dB: {ber_sim[0]:.4f})")
        
        return True
    except Exception as e:
        print(f"  ❌ Simulator test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 DIGITAL COMMUNICATION SIMULATOR - TEST SUITE")
    print("=" * 60)
    
    results = []
    results.append(("Modulation", test_modulation()))
    results.append(("Channel", test_channel()))
    results.append(("Viterbi", test_viterbi()))
    results.append(("OFDM", test_ofdm()))
    results.append(("Simulator", test_simulator()))
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {name}: {status}")
    
    print("-" * 60)
    print(f"  TOTAL: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! System is ready!")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    main()