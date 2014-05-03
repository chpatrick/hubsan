from hubsan import *
import logging
import math

logging.basicConfig(level = logging.INFO)

hubsan = Hubsan()
hubsan.init()
hubsan.bind()
hubsan.safety()

print "bind complete"

while True:
  hubsan.control(0.05, 0, 0, 0)