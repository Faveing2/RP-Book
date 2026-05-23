import numpy as np
from scipy.io.wavfile import write
import math

from mfsk_mod_demod import mfsk_demodulate
from mfsk_mod_demod import mfsk_modulate

def add_awgn(signal, snr_db):
    power_signal = np.mean(signal**2)
    snr_linear = 10**(snr_db / 10)
    noise_power = power_signal / snr_linear

    noise = np.sqrt(noise_power) * np.random.randn(len(signal))
    return signal + noise

FILE = "SCP_Database_-_Phase.html"
data = None

ascii_table = {i: chr(i) for i in range(128)}
char_to_ascii = {chr(i): i for i in range(128)}

with open(FILE, "r") as file:
    data = file.read()
    file.close()

bitstream = []
for char in data:
    try:
        bits = format(char_to_ascii[char], "08b")
    
        for bit in bits:
            bitstream.append(bit)
    except KeyError:
        for bit in ["0","0","0","0","0","0","0","0"]:
            bitstream.append(bit)


frequencies = [
    1000, 1400, 1800, 2200,
    2600, 3000, 3400, 3800,
]

# frequencies = [
#     1000, 1400
# ]

bitstream_str = "111111111"

for bit in bitstream:
    bitstream_str += bit

signal, t, symbols = mfsk_modulate(
    bitstream=bitstream_str,
    frequencies=frequencies,
    baud=100,
    samplerate=16000,
    continuous_phase=True
)

with open("bitstream.txt", "w") as file:
    file.write(bitstream_str)
    file.close()

ascii_table = {i: chr(i) for i in range(128)}

arr_data = np.zeros(len(bitstream))

for index, char in enumerate(bitstream):
    arr_data[index] = int(char)

demodulated_bits = np.split(arr_data,len(arr_data)/8)

output_text = ""
for char in demodulated_bits:
  bitstring = ""
  for bit in char:
    bitstring = bitstring +str(int(bit))
    
  #print(bitstring)
  try:
    output_text = output_text + ascii_table[int(bitstring,2)]
    #print(ascii_table[int(bitstring,2)])
  except KeyError:
    output_text = output_text + "?"

#print(demodulated_bits[0:5])
print(output_text)

#modulated_signal = bfsk_signal(bitstream,200,500,1200,44000,noise=False, noise_level=0)
#print(modulated_signal)
audio_scaled = (signal * 32767).astype(np.int16)
write(FILE+'.wav', 16000, audio_scaled)
