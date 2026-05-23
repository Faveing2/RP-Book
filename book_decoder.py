import numpy as np
import math
from scipy.io import wavfile
from mfsk_mod_demod import mfsk_demodulate
from mfsk_mod_demod import mfsk_modulate

frequencies = [
    1000, 1400, 1800, 2200,
    2600, 3000, 3400, 3800,
    4200, 4600, 5000, 5400,
    5800, 6200, 6600, 6800
]

# frequencies = [
#     1000, 1400
# ]

FILE = "SCP_Database_-_Phase.html.wav"
FILE = "tx (100baud 16k 16fsk)(all 1s).wav"

from scipy.io import wavfile

# Read the file
sample_rate, signal = wavfile.read(FILE)

# If the file is stereo, it will be (N, 2); flatten it to 1D
if len(signal.shape) > 1:
    signal = signal.flatten()

recovered_bits, rx_symbols = mfsk_demodulate(
    signal=signal,
    frequencies=frequencies,
    baud=100,
    samplerate=16000
)

bitstream_str = None
with open("bitstream.txt", "r") as file:
    bitstream_str = file.read()
    file.close()

### Calculate offset

pre_length = len("010101010")

#print(recovered_bits)

offset=0

for index, bit in enumerate(recovered_bits):
    try:
        if (recovered_bits[index] == "1" and recovered_bits[index+1] == "1" and recovered_bits[index+2] == "1" and recovered_bits[index+3] == "1" and recovered_bits[index+4] == "1" and recovered_bits[index+5] == "1" and recovered_bits[index+6] == "1" and recovered_bits[index+7] == "1" and recovered_bits[index+8] == "1"):
            offset = index+9
            break
    except IndexError:
       break
# offset_end = len(recovered_bits)

# for index, bit in enumerate(recovered_bits):
#     try:
#         if (recovered_bits[index] == "0" and recovered_bits[index+1] == "0" and recovered_bits[index+2] == "0" and recovered_bits[index+3] == "0" and recovered_bits[index+4] == "0" and recovered_bits[index+5] == 0 and recovered_bits[index+6] == 0 and recovered_bits[index+7] == 0 and recovered_bits[index+8] == 0 and recovered_bits[index+9] == 0):
#             offset_end = index+8
#             break
#     except IndexError:
#         break

print(offset)
#print(offset_end)
errors = 0

shifted_src = bitstream_str[pre_length:]
shifted_recovered = recovered_bits[offset:]

try:
    for index, tx_bit in enumerate(bitstream_str[0:5000]):
        rx_bit = recovered_bits[index]
        if tx_bit != rx_bit:
            errors += 1
except IndexError:
    pass

#print(recovered_bits)

print("BER", errors/len(bitstream_str))

# print(bitstream_str[0:100])
# print(recovered_bits[0:100])

#print(shifted_src[0:100])
#print(shifted_recovered[0:100])

ascii_table = {i: chr(i) for i in range(128)}
char_to_ascii = {chr(i): i for i in range(128)}

arr_data = np.zeros(len(shifted_recovered))

for index, char in enumerate(shifted_recovered):
    arr_data[index] = int(char)

#demodulated_bits = np.split(arr_data,len(arr_data)/8)
demodulated_bits = arr_data[:len(arr_data)//8*8].reshape(-1, 8)

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

print(recovered_bits)