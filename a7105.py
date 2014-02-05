from mpsse import *
import time
from struct import *

REG_GIO1S = 0x0b

CONST_4WIRE = 0x19

class A7105:
  def init(self):
    self.spi = MPSSE(SPI0, TEN_MHZ, MSB)
    self.write_reg(REG_GIO1S, CONST_4WIRE)

  def write_reg(self, reg, value):
    self.spi.Start()
    self.spi.Write(pack('BB', reg, value))
    self.spi.Stop()

  def read_reg(self, reg):
    self.spi.Start()
    self.spi.Write(pack('B', 0x40 | reg))
    value = unpack('B', self.spi.Read(1))[0]
    self.spi.Stop()
    return value

  def reset(self):
    self.write_reg(0, 0)

a7105 = A7105()
a7105.init()
time.sleep(1)
time.sleep(1)
for r in xrange(256):
  val = a7105.read_reg(r)
  print r, val
  time.sleep(0.2)