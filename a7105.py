from mpsse import *
import time
from struct import *

class Reg:
  MODE  = 0x00 # reset, etc
  ID    = 0x06 # used to set transmitter ID
  GIO1S = 0x0b # enables 4-wire SPI

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
    self.spi_on = SPIContext(self.spi)
    self.write_reg(Reg.GIO1S, ENABLE_4WIRE)

  def write_reg(self, reg, value):
    with self.spi_on:
      self.spi.Write(pack('BB', reg, value))

  def read_reg(self, reg):
    value = None
    with self.spi_on:
      self.spi.Write(pbyte(READ_BIT | reg))
      value = ubyte(self.spi.Read(1))
    return value

  def reset(self):
    self.write_reg(Reg.MODE, 0x00)

  def write_id(self, id):
    with self.spi_on:
      self.spi.Write(pbyte(Reg.ID) + id)

a7105 = A7105()
a7105.init()
time.sleep(1)
for r in xrange(256):
  val = a7105.read_reg(r)
  print r, bin(val)
  time.sleep(0.05)