from mpsse import *
import time
from struct import *
import logging

class Reg:
  # reset, etc
  MODE         = 0x00
  # used to set transmitter options
  MODE_CONTROL = 0x01
  # used to set the FIFO end pointer (FEP)
  FIFO_1       = 0x03
  # used to set transmitter ID
  ID           = 0x06
  # enables 4-wire SPI
  GIO1S        = 0x0b
  # clock settings
  CLOCK        = 0x0d
  # controls data rate division
  DATA_RATE    = 0x0e
  # controls frequency deviation
  TX_II        = 0x15
  # controls receiver settings
  RX           = 0x18
  # more receiver settings
  RX_GAIN_I    = 0x19
  # reserved constants
  RX_GAIN_IV   = 0x1C
  # encoding settings
  CODE_I       = 0x1F
  # more encoding settings
  CODE_II      = 0x20
  # RX demodulator settings
  RX_DEM_TEST  = 0x29

class State:
  SLEEP               = 0x80
  IDLE                = 0x90
  STANDBY             = 0xA0
  PLL                 = 0xB0
  RX                  = 0xC0
  TX                  = 0xD0
  RESET_WRITE_POINTER = 0xE0
  RESET_READ_POINTER  = 0xF0

READ_BIT = 0x40 # flag bit specifying register should be read

ENABLE_4WIRE = 0x19 # value written to GIO1S to enable 4-wire SPI

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

class A7105:
  def init(self):
    self.spi = MPSSE(SPI0, TEN_MHZ, MSB)
    self.cs_low = SPIContext(self.spi)
    self.write_reg(Reg.GIO1S, ENABLE_4WIRE)

  def write_reg(self, reg, value):
    with self.cs_low:
      self.spi.Write(pack('BB', reg, value))

    logging.debug('writeReg(%02x, %02x)' % ( reg, value ))

  def read_reg(self, reg):
    value = None
    with self.cs_low:
      self.spi.Write(pbyte(READ_BIT | reg))
      value = ubyte(self.spi.Read(1))
    return value

  def reset(self):
    self.write_reg(Reg.MODE, 0x00)

  def write_id(self, id):
    with self.cs_low:
      self.spi.Write(pbyte(Reg.ID) + id)

  def strobe(self, state):
    # A7105 datasheet says SCS should be high after only 4 bits,
    # but deviation doesn't bother
    with self.cs_low:
      self.spi.Write(pbyte(state))
'''
a7105 = A7105()
a7105.init()
for r in xrange(256):
  val = a7105.read_reg(r)
  print r, val
  time.sleep(0.05)
'''