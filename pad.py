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
hubsan.safety()

print "starting"

def map_axis(joystick, axis, input_min, input_max, output_min, output_max, default = 0.5):
  axis_val = joystick.get_axis(axis)

  output = None
  if input_min <= axis_val <= input_max or input_max <= axis_val <= input_min:
    output = (axis_val - input_min) / (input_max - input_min)
  else:
    output = default

  return output_min + output * (output_max - output_min)

while True:
  pygame.event.get()

  throttle = max(0, -joystick.get_axis(4))
  rudder   = joystick.get_axis(0)
  elevator = joystick.get_axis(1)
  aileron  = joystick.get_axis(3)

  hubsan.control(throttle, rudder, elevator, aileron)
