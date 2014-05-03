from a7105 import *
from hubsan import *
import itertools
import sys
import time

mpsse = MPSSE()
index = 0

# open the first possible device, up to 5
while True:
  if index == 5:
    raise Exception("No MPSSE device found.")

  try:
    mpsse.Open(0x0403, 0x6014, SPI0, frequency = TEN_MHZ, endianess = MSB, index = index)
    break
  except Exception:
    index += 1

r = A7105(mpsse)
r.init()
r.write_id(Hubsan.ID)

channel = None
session_id = None

def receive():
  r.strobe(State.RX)
  for recv_n in xrange(100):
    if r.read_reg(Reg.MODE) & 1 == 0:
      return r.read_data(16)
  return None

for chan in itertools.cycle(Hubsan.ALLOWED_CHANNELS):
  print "\rscanning channel %d" % chan,
  sys.stdout.flush()
  r.strobe(State.STANDBY)
  r.set_channel(chan)

  packet = receive()
  if packet:
    channel = packet[1]
    session_id = packet[2:6]
    break

print
print "channel: %d" % ubyte(channel)
print "session_id: %s" % format_packet(session_id)

last_packet_time = None

while True:
  packet = receive()
  if packet:
    if packet[0] == "\x03":
      r.write_id(session_id)
      print "stage 3 packet received, switching ID"

    now = time.time()
    elapsed = now - last_packet_time if last_packet_time else 0 
    last_packet_time = now
    print "%3.0f ms %s" % (elapsed * 1000, format_packet(packet))
