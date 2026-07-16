# Digital Communication Simulator

A modular digital communication simulation framework built in Python to demonstrate the complete
transmit–channel–receive pipeline used in modern wireless communication systems. The project focuses
on practical implementation of digital modulation, noisy channel modeling, receiver design, and
communication performance analysis while following modular software engineering principles.

---

## What this project proves

- You can implement digital modulation schemes from first principles instead of relying on toolbox functions.
- You can simulate realistic communication channels using statistical noise models.
- You can evaluate communication system performance using engineering metrics such as BER.
- You can design a modular DSP framework that is easily extendable toward LTE, 5G NR, OFDM, and SDR applications.
- You can validate communication algorithms against theoretical digital communication principles.

---

## Architecture at a glance

- **Source**: Random binary information generation.
- **Transmitter**: BPSK / QPSK symbol mapping with Gray coding.
- **Channel**: Additive White Gaussian Noise (AWGN) model.
- **Receiver**: Maximum Likelihood Detection and symbol recovery.
- **Performance Analysis**: BER computation and communication statistics.
- **Visualization**: Constellation diagrams and waveform analysis.

Primary references:

- `docs/architecture.md`
- `docs/mathematical_model.md`
- `ENGINEERING_RETROSPECTIVE.txt`

---

## Quick verification

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run the simulator

```bash
python main.py
```

### Run an example simulation

```bash
python examples/bpsk_awgn.py
```

Expected output

```
Modulation : BPSK

SNR : 10 dB

BER : 0.00078
```

Constellation and waveform plots should automatically appear after the simulation.

---

## Supported Features

- Random Bit Stream Generation
- BPSK Modulation
- QPSK Modulation
- Gray Coding
- Complex Baseband Signal Representation
- AWGN Channel
- Maximum Likelihood Receiver
- Bit Error Rate (BER) Calculation
- Constellation Diagram Visualization
- Modular Communication Pipeline
- NumPy Vectorized Processing

---

## Build Architecture

```
Random Bit Generator

↓

Digital Modulator

↓

Complex Baseband Symbols

↓

AWGN Channel

↓

Receiver

↓

BER Evaluation

↓

Visualization
```

---

## Module Map

- `source/` – Random bit generation and source data.
- `modulation/` – BPSK, QPSK, and future modulation schemes.
- `channel/` – AWGN channel implementation and future fading models.
- `receiver/` – Demodulation and decision algorithms.
- `metrics/` – BER and communication performance metrics.
- `visualization/` – Constellation plots and waveform visualization.
- `utils/` – Shared DSP utility functions.
- `config/` – Simulation parameters and configuration.
- `examples/` – Example simulations.

---

## Engineering Decisions and Trade-offs

- **Complex Baseband Representation**: Chosen over passband simulation to reduce computational complexity while preserving signal information.
- **Gray Coding**: Used in QPSK to minimize bit errors caused by neighbouring symbol decisions.
- **Symbol Energy Normalization**: Ensures fair BER comparison across different modulation schemes.
- **AWGN First Approach**: Provides the industry-standard baseline before extending to fading channels.
- **NumPy Vectorization**: Improves performance by replacing Python loops with optimized numerical operations.
- **Modular Architecture**: Enables new modulation techniques and channel models without redesigning the simulator.

---

## Engineering Validation

The simulator validates communication algorithms by verifying that

- BER decreases as SNR increases.
- Higher noise produces wider constellation spreading.
- Gray coding reduces bit errors.
- Maximum Likelihood Detection minimizes decision errors under AWGN.
- Simulated behaviour agrees with standard digital communication theory.

---

## Future Roadmap

- 16-QAM
- 64-QAM
- Rayleigh Fading Channel
- Rician Fading Channel
- Raised Cosine Pulse Shaping
- Root Raised Cosine Receiver Filter
- OFDM Transmitter and Receiver
- Adaptive Modulation
- Convolutional Coding
- Viterbi Decoder
- Reed–Solomon Coding
- LDPC Coding
- MIMO Simulation
- Channel Estimation
- Carrier Synchronization
- Timing Recovery
- GNU Radio Integration
- Software Defined Radio (HackRF / USRP)

---

## Evidence and Results

The simulator produces

- BER Measurements
- Constellation Diagrams
- Received Signal Waveforms
- Communication Performance Statistics

Future versions will include

- BER vs SNR plots
- Eye diagrams
- Power Spectral Density analysis
- Automated regression tests for communication performance

---

## Limits and Boundaries

- Current implementation focuses on baseband digital communication.
- Multipath fading and channel coding are planned but not yet implemented.
- The simulator is intended as an educational and engineering framework rather than a standards-compliant LTE/5G PHY implementation.
- Carrier synchronization, timing recovery, and SDR hardware integration remain future enhancements.

---

## Deep-Dive Documentation

- `docs/architecture.md` – Communication pipeline and software architecture.
- `docs/mathematical_model.md` – Mathematical derivations of modulation and BER.
- `docs/results.md` – Simulation results and performance analysis.
- `ENGINEERING_RETROSPECTIVE.txt` – Engineering decisions, trade-offs, and lessons learned.

---

## Technologies Used

- Python
- NumPy
- SciPy
- Matplotlib

---

## License

MIT License.

---

## Author

**Rudra Bishwakarma**

B.Tech Electronics & Communication Engineering

Jaypee University of Engineering & Technology

GitHub: https://github.com/RudraBishwakarma
