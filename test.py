from hubsan import *
import logging
import math

logging.basicConfig(level = logging.INFO)

hubsan = Hubsan()
hubsan.init()
hubsan.bind()
hubsan.safety()

print "bind complete"
