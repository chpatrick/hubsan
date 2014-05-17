from a7105 import *
import time
import logging
import random
import struct
import math
import random

def calc_checksum(packet):
  total = 0
  for char in packet:
    total += struct.unpack('B', char)[0]
  return (256 - (total % 256)) & 0xff

# linear interpolation
def lerp(t, min, max):
  return int(round(min + t * (max - min)))

# linear interpolation with probabilistic rounding
def lerp_random(t, min, max):
  val = min + t * (max - min)
  val_floor = int(val)
  offset = val - val_floor
  return val_floor if random.random() > offset else val_floor + 1

log = logging.getLogger('hubsan')

class BindError(Exception):
  pass

class Hubsan:
  # not sure if byte order is correct
  ID = '\x55\x20\x10\x41' # doesn't respond without this
  CALIBRATION_MAX_CHECKS = 3
  # channels we can use, magic numbers from deviation
  ALLOWED_CHANNELS = [ 0x14, 0x1e, 0x28, 0x32, 0x3c, 0x46, 0x50, 0x5a, 0x64, 0x6e, 0x78, 0x82 ]
  # mystery packet constants
  MYSTERY_CONSTANTS = '\x08\xe4\xea\x9e\x50' # does respond without this?
  # mystery ID from deviation
  TX_ID = '\xdb\x04\x26\x79' # also reacts without this

  def __init__(self, a7105 = None):
    self.a7105 = a7105

  def init(self):
    if self.a7105 == None:
      self.a7105 = A7105()

      self.a7105.init()

  def send_packet(self, packet):
    self.a7105.strobe(State.STANDBY)
    self.a7105.write_data(packet)
    self.a7105.strobe(State.TX)
    #time.sleep(0.003)

    time.sleep(0.002)
    for send_n in xrange(4):
      if self.a7105.read_reg(Reg.MODE) & 1 == 0:
        return

    raise Exception("Sending did not complete.")

  def bind_stage(self, state):
    log.debug('bind stage %d' % state)

    packet = struct.pack('BB', state, self.channel)
    packet += self.session_id
    packet += '\x00' * 9
    packet += pbyte(calc_checksum(packet))

    self.send_packet(packet)
    send_time = time.time()

    self.a7105.strobe(State.RX)

    # poll for 15 ms for the response
    while time.time() < send_time + 0.015:
      if self.a7105.read_reg(Reg.MODE) & 1 == 0:
        packet = self.a7105.read_data(16)
        log.debug('got response: %s', format_packet(packet))
        if packet[0] == '\xe0' or packet[0] == '\xe1':
          raise BindError()

        return packet

    raise BindError()

  def handshake(self):
    while True:
      try:
        self.bind_stage(1)
        state4_response = self.bind_stage(3)
        self.a7105.write_id(state4_response[2:6])
        self.bind_stage(1)

        break
      except BindError:
        continue

    while True:
      try:
        phase2_response = self.bind_stage(9)
        if phase2_response[1] == '\x09':
          break
      except BindError:
        continue

  def bind(self, session_id = None, channel = None):
    if session_id and channel: # resuming
      log.info('resuming session')
      self.session_id = session_id
      self.channel = channel
      self.a7105.write_id(session_id)
      self.a7105.set_channel(self.channel)
    else:
      log.info('binding started')
      # generate a random session ID
      self.session_id = struct.pack('BBBB', *(random.randint(0, 255) for n in xrange(4)))

      # choose a random channel
      self.channel, = random.sample(Hubsan.ALLOWED_CHANNELS, 1)

      self.a7105.write_id(Hubsan.ID)

      self.a7105.set_channel(self.channel)
      self.handshake()
      time.sleep(0.5) # wait a little bit until we can send control signals
      log.info('bind complete!')

    # enable CRC, id code length 4, preamble length 4
    self.a7105.write_reg(Reg.CODE_I, 0x0F)

  def control_raw(self, throttle, rudder, elevator, aileron, leds = True, flips = False):
    control_packet = '\x20'
    for chan in [ throttle, rudder, elevator, aileron ]:
      control_packet += '\x00' + pbyte(chan)
    flags = 0x02 | (0 if leds else 0x04) | (0x08 if flips else 0)
    control_packet += pbyte(flags) + '\x64' + Hubsan.TX_ID
    control_packet += pbyte(calc_checksum(control_packet))

    log.debug('sending control packet: %s', format_packet(control_packet))

    for i in xrange(4):
      #self.send_packet(control_packet, self.channel)
      self.a7105.strobe(State.STANDBY)
      self.a7105.write_data(control_packet)
      self.a7105.strobe(State.TX)
      time.sleep(0.003)
    #self.send_packet(control_packet, self.channel + 0x23)
    self.a7105.strobe(State.STANDBY)

    self.a7105.set_channel(self.channel + 0x23)
    self.a7105.write_data(control_packet)
    self.a7105.strobe(State.TX)
    time.sleep(0.003)
    self.a7105.set_channel(self.channel)

  '''
    Send a control packet using floating point values.
    Throttle ranges from 0 to 1, all others range from -1 to 1.
  '''
  def control(self, throttle, rudder, elevator, aileron, leds = True, flips = False):
    throttle_raw = lerp(throttle, 0x00, 0xFF)
    rudder_raw = lerp((rudder + 1) / 2, 0x34, 0xCC)
    elevator_raw = lerp((elevator + 1) / 2, 0x3E, 0xBC)
    aileron_raw = lerp((-aileron + 1) / 2, 0x45, 0xC3)
    self.control_raw(throttle_raw, rudder_raw, elevator_raw, aileron_raw, leds, flips)

  def control_random(self, throttle, rudder, elevator, aileron, leds = True, flips = False):
    throttle_raw = lerp_random(throttle, 0x00, 0xFF)
    rudder_raw = lerp_random((rudder + 1) / 2, 0x34, 0xCC)
    elevator_raw = lerp_random((elevator + 1) / 2, 0x3E, 0xBC)
    aileron_raw = lerp_random((-aileron + 1) / 2, 0x45, 0xC3)
    self.control_raw(throttle_raw, rudder_raw, elevator_raw, aileron_raw, leds, flips)

  '''
    As a safety measure, the Hubsan X4 will not accept control commands until
    the throttle has been set to 0 for a number of cycles. Calling this function
    will send the appropriate control signals.
  '''
  def safety(self):
    log.info('sending safety signals')
    for i in xrange(100):
      self.control(0, 0, 0, 0) # send 0 throttle for 100 cycles
    log.info('safety complete')

  def close(self):
    self.a7105.close()