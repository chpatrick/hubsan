from hubsan import *
import logging
import math

logging.basicConfig(level = logging.INFO)

hubsan = Hubsan()
hubsan.init()
hubsan.bind()
hubsan.safety()

print "bind complete"

session_id = hubsan.session_id
channel = hubsan.channel

print "channel: %d" % channel
print "session_id: %s" % format_packet(session_id)

print "closing, press any key"
raw_input()
hubsan.close()

hubsan2 = Hubsan()
hubsan2.init()
hubsan2.bind(session_id = session_id, channel = channel)

print "resumed"

while True:
  hubsan2.control(0.05, 0, 0, 0)
