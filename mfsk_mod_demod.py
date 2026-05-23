import numpy as np
import math

def goertzel(samples, target_freq, samplerate):
    """
    Compute energy at a target frequency using the Goertzel algorithm.
    """

    N = len(samples)

    k = int(0.5 + (N * target_freq) / samplerate)

    omega = (2.0 * np.pi * k) / N

    coeff = 2.0 * np.cos(omega)

    s_prev = 0.0
    s_prev2 = 0.0

    for sample in samples:
        s = sample + coeff * s_prev - s_prev2
        s_prev2 = s_prev
        s_prev = s

    power = (
        s_prev2**2
        + s_prev**2
        - coeff * s_prev * s_prev2
    )

    return power


def mfsk_demodulate(
    signal,
    frequencies,
    baud,
    samplerate
):
    """
    General MFSK demodulator using Goertzel detection.

    Parameters
    ----------
    signal : ndarray
        Input MFSK signal

    frequencies : list or ndarray
        Symbol frequencies

    baud : float
        Symbol rate in symbols/sec

    samplerate : float
        Sample rate in Hz

    Returns
    -------
    recovered_bits : str
        Recovered bitstream

    recovered_symbols : list
        Recovered symbol indices
    """

    M = len(frequencies)

    bits_per_symbol = math.log2(M)

    if not bits_per_symbol.is_integer():
        raise ValueError(
            "Number of frequencies must be a power of 2"
        )

    bits_per_symbol = int(bits_per_symbol)

    samples_per_symbol = int(samplerate / baud)

    num_symbols = len(signal) // samples_per_symbol

    recovered_symbols = []

    for i in range(num_symbols):

        start = i * samples_per_symbol
        end = start + samples_per_symbol

        symbol_chunk = signal[start:end]

        # Compute energy at each frequency
        energies = []

        for freq in frequencies:
            power = goertzel(
                symbol_chunk,
                freq,
                samplerate
            )
            energies.append(power)

        # Pick strongest frequency
        detected_symbol = np.argmax(energies)

        recovered_symbols.append(detected_symbol)

    # Convert symbols back to bits
    recovered_bits = ""

    for sym in recovered_symbols:

        recovered_bits += format(
            sym,
            f"0{bits_per_symbol}b"
        )

    return recovered_bits, recovered_symbols

def add_awgn(signal, snr_db):
    power_signal = np.mean(signal**2)
    snr_linear = 10**(snr_db / 10)
    noise_power = power_signal / snr_linear

    noise = np.sqrt(noise_power) * np.random.randn(len(signal))
    return signal + noise

def mfsk_modulate(
    bitstream,
    frequencies,
    baud,
    samplerate,
    amplitude=1.0,
    continuous_phase=True
):
    """
    General MFSK modulator.

    Parameters
    ----------
    bitstream : str
        String of bits, e.g. "101100101"

    frequencies : list or ndarray
        List of frequencies for each symbol state.
        Example for 8FSK:
            [1000, 1400, 1800, 2200,
             2600, 3000, 3400, 3800]

    baud : float
        Symbol rate in symbols/sec

    samplerate : float
        Sampling rate in Hz

    amplitude : float
        Signal amplitude

    continuous_phase : bool
        Maintain phase continuity between symbols

    Returns
    -------
    signal : ndarray
        Modulated waveform

    t : ndarray
        Time axis

    symbols : list
        Symbol indices used
    """

    M = len(frequencies)

    # Ensure M is power of 2
    bits_per_symbol = math.log2(M)
    if not bits_per_symbol.is_integer():
        raise ValueError("Number of frequencies must be a power of 2")

    bits_per_symbol = int(bits_per_symbol)

    # Pad bitstream if necessary
    remainder = len(bitstream) % bits_per_symbol
    if remainder != 0:
        padding = bits_per_symbol - remainder
        bitstream += "0" * padding

    # Split into symbols
    symbols = []
    for i in range(0, len(bitstream), bits_per_symbol):
        chunk = bitstream[i:i + bits_per_symbol]
        symbols.append(int(chunk, 2))

    samples_per_symbol = int(samplerate / baud)

    signal = []
    phase = 0.0

    for sym in symbols:

        freq = frequencies[sym]

        t_symbol = np.arange(samples_per_symbol) / samplerate

        # Generate symbol waveform
        symbol_wave = amplitude * np.sin(
            2 * np.pi * freq * t_symbol + phase
        )

        signal.extend(symbol_wave)

        # Maintain continuous phase
        if continuous_phase:
            phase += (
                2 * np.pi
                * freq
                * samples_per_symbol
                / samplerate
            )

            # Keep phase bounded
            phase = np.mod(phase, 2 * np.pi)

    signal = np.array(signal)

    t = np.arange(len(signal)) / samplerate

    return signal, t, symbols