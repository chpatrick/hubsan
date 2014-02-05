from a7105 import *

class Hubsan:
  # not sure if byte order is correct
  ID = '\x55\x20\x10\x41'

  def __init__(self):
    self.a7105 = A7105()

  def init(self):
    a = self.a7105

    a.init()

    a.write_id(Hubsan.ID)
    # set various radio options
    a.write_reg(Reg.MODE_CONTROL, 0x63)
    # set packet length (FIFO end pointer) to 0x0f + 1 == 16
    a.write_reg(Reg.FIFO_1, 0x0f)
    # select crystal oscillator and system clock divider of 1/2
    a.write_reg(Reg.CLOCK, 0x05)
    # set data rate division to Fsyck / 32 / 5
    a.write_reg(Reg.DATA_RATE, 0x04)
    # set Fpfd to 32 MHz
    a.write_reg(Reg.TX_II, 0x2b)
    # select BPF bandwidth of 500 KHz and up side band
    a.write_reg(Reg.RX, 0x62)
    # enable manual VGA calibration
    a.write_reg(Reg.RX_GAIN_I, 0x80)
    # set some reserved constants
    a.write_reg(Reg.RX_GAIN_IV, 0x0A)
    # select ID code length of 4, preamble length of 4
    a.write_reg(Reg.CODE_I, 0x07)
    # set demodulator DC estimation average mode,
    # ID code error tolerance = 1 bit, 16 bit preamble pattern detection length
    a.write_reg(Reg.CODE_II, 0x17)
    # set constants
    a.write_reg(Reg.RX_DEM_TEST, 0x47)

    # go into Standby mode
    a.strobe(State.STANDBY)

logging.basicConfig(level = logging.DEBUG)

hubsan = Hubsan()
hubsan.init()