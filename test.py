from hubsan import *
import logging
import math

logging.basicConfig(level = logging.INFO)

hubsan = Hubsan()
hubsan.init()
hubsan.bind()
time.sleep(2)

for i in xrange(100):
  hubsan.control(0x00, 0x80, 0x7d, 0x84)

print "throttling up"

x = 0

while True:
  x += 0.05
  hubsan.control(int((math.sin(x) + 1) * 127.5), 0x80, 0x7d, 0x84)
