from mpsse import *
import time
from struct import *
import logging

# generate inverse mapping from 'enum' class, for debugging
def debug_enum(enum):
  debug = {}
  for k, v in enum.__dict__.items():
    if type(v) is int:
      debug[v] = k
  return debug

class Reg:
  # reset, etc
  MODE              = 0x00
  # used to set transmitter options
  MODE_CONTROL      = 0x01
  # used to select calibration mode
  CALIBRATION       = 0x02
  # used to set the FIFO end pointer (FEP)
  FIFO_1            = 0x03
  # used to set transmitter ID
  ID                = 0x06
  # enables 4-wire SPI
  GIO1S             = 0x0b
  # clock settings
  CLOCK             = 0x0d
  # controls data rate division
  DATA_RATE         = 0x0e
  # channel number select
  PLL_I             = 0x0f
  # controls frequency deviation
  TX_II             = 0x15
  # controls receiver settings
  RX                = 0x18
  # more receiver settings
  RX_GAIN_I         = 0x19
  # reserved constants
  RX_GAIN_IV        = 0x1C
  # encoding settings
  CODE_I            = 0x1F
  # more encoding settings
  CODE_II           = 0x20
  # contains flag for checking IF calibration
  IF_CALIBRATION_I  = 0x22
  # contains flag for checking VCO calibration
  VCO_CALIBRATION_I = 0x25
  # TX power settings
  TX_TEST           = 0x28
  # RX demodulator settings
  RX_DEM_TEST       = 0x29

debug_reg = debug_enum(Reg)

class State:
  SLEEP               = 0x80
  IDLE                = 0x90
  STANDBY             = 0xA0
  PLL                 = 0xB0
  RX                  = 0xC0
  TX                  = 0xD0
  RESET_WRITE_POINTER = 0xE0
  RESET_READ_POINTER  = 0xF0

debug_state = debug_enum(State)

class Power:
  _100uW = 0
  _300uW = 1
  _1mW   = 2
  _3mW   = 3
  _10mW  = 4
  _30mW  = 5
  _100mW = 6
  _150mW = 7

debug_power = debug_enum(Power)

# contains PAC and TBG values
power_enums = {}

power_enums[Power._100uW] = ( 0, 0 )
power_enums[Power._300uW] = ( 0, 1 ) # datasheet recommended
power_enums[Power._1mW]   = ( 0, 2 )
power_enums[Power._3mW]   = ( 0, 4 )
power_enums[Power._10mW]  = ( 1, 5 )
power_enums[Power._30mW]  = ( 2, 7 ) # looks like a good value
power_enums[Power._100mW] = ( 3, 7 ) # datasheet recommended
power_enums[Power._150mW] = ( 3, 7 ) # datasheet recommended

READ_BIT = 0x40 # flag bit specifying register should be read

ENABLE_4WIRE = 0x19 # value written to GIO1S to enable 4-wire SPI

FIFO_START = 0x05

# context guard for SPI
class SPIContext:
  def __init__(self, spi):
    self.spi = spi

  def __enter__(self):
    self.spi.Start()

  def __exit__(self, type, value, traceback):
    self.spi.Stop()
    return False

# pack a byte
def pbyte(byte):
  return pack('B', byte)

# unpack a byte
def ubyte(bytestring):
  return unpack('B', bytestring)[0]

def format_packet(packet):
  return ' '.join('%02x' % ubyte(byte) for byte in packet)

log = logging.getLogger('a7105')

class A7105:
  def __init__(self, spi = None):
    self.spi = spi

  def init(self):
    if self.spi == None:
      self.spi = MPSSE(SPI0, TEN_MHZ, MSB)
    self.cs_low = SPIContext(self.spi)

    self.reset()

    self.write_reg(Reg.GIO1S, ENABLE_4WIRE)

    self.init_regs()

    # go into PLL mode like the datasheet saysk
    # self.strobe(State.PLL)

    self.calibrate_if()
    self.calibrate_vco(0x00)
    self.calibrate_vco(0xa0)

    self.strobe(State.STANDBY)

    # deviation code seems to set up GPIO pins here, looks device-specific
    # we use GPIO1 for 4-wire SPI anyway

    # seems like a reasonable power level
    self.set_power(Power._30mW)

    # not sure what this is for
    self.strobe(State.STANDBY)

  def init_regs(self):
    log.debug('initializing registers')

    # set various radio options
    self.write_reg(Reg.MODE_CONTROL, 0x63)
    # set packet length (FIFO end pointer) to 0x0f + 1 == 16
    self.write_reg(Reg.FIFO_1, 0x0f)
    # select crystal oscillator and system clock divider of 1/2
    self.write_reg(Reg.CLOCK, 0x05)
    if self.read_reg(Reg.CLOCK) != 0x05:
      raise Exception('Could not read back register - sanity check failed. Check wiring.')

    # set data rate division to Fsyck / 32 / 5
    self.write_reg(Reg.DATA_RATE, 0x04)
    # set Fpfd to 32 MHz
    self.write_reg(Reg.TX_II, 0x2b)
    # select BPF bandwidth of 500 KHz and up side band
    self.write_reg(Reg.RX, 0x62)
    # enable manual VGA calibration
    self.write_reg(Reg.RX_GAIN_I, 0x80)
    # set some reserved constants
    self.write_reg(Reg.RX_GAIN_IV, 0x0A)
    # select ID code length of 4, preamble length of 4
    self.write_reg(Reg.CODE_I, 0x07)
    # set demodulator DC estimation average mode,
    # ID code error tolerance = 1 bit, 16 bit preamble pattern detection length
    self.write_reg(Reg.CODE_II, 0x17)
    # set constants
    self.write_reg(Reg.RX_DEM_TEST, 0x47)

  # WTF: these seem to differ from the A7105 spec, this is the deviation version
  def calibrate_if(self):
    log.debug('calibrating IF bank')

    # select IF calibration
    self.write_reg(Reg.CALIBRATION, 0b001)

    # WTF: deviation reads calibration here, not sure why
    calib_n = 0
    # should only take 256 microseconds, but try a few times anyway
    while True:
      if calib_n == 3:
        raise Exception("IF calibration did not complete.")
      elif self.read_reg(Reg.CALIBRATION) & 0b001 == 0:
        break
      time.sleep(0.001)
      calib_n += 1

    # check calibration succeeded
    if self.read_reg(Reg.IF_CALIBRATION_I) & 0b1000 != 0:
      raise Exception("IF calibration failed.")
    log.debug('calibration complete')

  def calibrate_vco(self, channel):
    log.debug('calibrating VCO channel %02x' % (channel))
    # reference code sets 0x24, 0x26 here, deviation skips

    self.write_reg(Reg.PLL_I, channel)

    # select VCO calibration
    self.write_reg(Reg.CALIBRATION, 0b010)

    for calib_n in xrange(4):
      if calib_n == 3:
        raise Exception("VCO calibration did not complete.")
      elif self.read_reg(Reg.CALIBRATION) & 0b010 == 0:
        break
      time.sleep(0.001)

    # check calibration succeeded
    if self.read_reg(Reg.VCO_CALIBRATION_I) & 0b1000 != 0:
      raise Exception("VCO calibration failed.")
    log.debug('calibration complete')

  def write_reg(self, reg, value):
    log.debug('write_reg({0}, {1:02x} == {2:08b})'.format( debug_reg[reg], value, value ))
    with self.cs_low:
      self.spi.Write(pack('BB', reg, value))

  def read_reg(self, reg):
    value = None
    with self.cs_low:
      self.spi.Write(pbyte(READ_BIT | reg))
      value = ubyte(self.spi.Read(1))
    log.debug('read_reg({0}) == {1:02x} == {2:08b}'.format( debug_reg[reg], value, value ) )
    return value

  # software reset
  # seems to make the A7105 unresponsive :/
  def reset(self):
    log.debug('reset()')
    self.write_reg(Reg.MODE, 0x00)

  def write_id(self, id):
    log.debug('write_id(%s)' % format_packet(id))
    with self.cs_low:
      self.spi.Write(pbyte(Reg.ID) + id)

  def strobe(self, state):
    # A7105 datasheet says SCS should be high after only 4 bits,
    # but deviation doesn't bother
    log.debug('strobe(%s)' % debug_state[state])
    with self.cs_low:
      self.spi.Write(pbyte(state))

  def set_power(self, power):
    log.debug('set_power(%s)' % debug_power[power])
    pac, tbg = power_enums[power]
    self.write_reg(Reg.TX_TEST, (pac << 3) | tbg)

  def write_data(self, packet, channel):
    log.debug('write_data(%s, %02x)' % ( format_packet(packet), channel ))
    # deviation does this all under one SPI session, I think it should be fine
    self.strobe(State.RESET_WRITE_POINTER)
    with self.cs_low:
      self.spi.Write(pbyte(FIFO_START) + packet)

    # select the channel
    # WTF: do we need to do this here?
    self.write_reg(Reg.PLL_I, channel)

    # transmit the data
    self.strobe(State.TX)

  def read_data(self, length):
    self.strobe(State.RESET_READ_POINTER)
    packet = None
    with self.cs_low:
      self.spi.Write(pbyte(READ_BIT | FIFO_START))
      packet = self.spi.Read(length)
    
    log.debug('read_data(%d) == %s' % ( length, format_packet(packet) ))

    return packet
