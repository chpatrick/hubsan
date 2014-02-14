import logging
from hubsan import *
import pygame
import pygame.event
import pygame.joystick

pygame.init()

pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)

joystick.init()

logging.basicConfig(level = logging.INFO)

hubsan = Hubsan()
hubsan.init()
hubsan.bind()
time.sleep(2)

for i in xrange(100):
  hubsan.control(0x00, 0x80, 0x7d, 0x84)

print "starting"

PITCH_MIN = 0x3e
PITCH_MAX = 0xbc

def map_axis(joystick, axis, input_min, input_max, output_min, output_max, default = 0.5):
  axis_val = joystick.get_axis(axis)

  output = None
  if input_min <= axis_val <= input_max or input_max <= axis_val <= input_min:
    output = (axis_val - input_min) / (input_max - input_min)
  else:
    output = default

  return output_min + output * (output_max - output_min)


throttle_val = 0
while True:
  pygame.event.get()

  throttle = int(map_axis(joystick, 4, -0.05, -1, 0x00, 0xFF, default = 0))
  elevator = int(map_axis(joystick, 1,  -1,  1, 0x3E, 0xBC))
  aileron  = int(map_axis(joystick, 3,   1, -1, 0x45, 0xC3))
  rudder   = int(map_axis(joystick, 0,  -1,  1, 0x34, 0xCC))

  #print "throttle: %f elevator: %f" % ( throttle, elevator )
  hubsan.control(throttle, rudder, elevator, aileron)
