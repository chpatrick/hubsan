from hubsan import *
import logging

logging.basicConfig(level = logging.INFO)

hubsan = Hubsan()
hubsan.init()
hubsan.bind()
time.sleep(2)
while True:
  hubsan.control(0xe0, 0x80, 0x7d, 0x84)
