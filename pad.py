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
hubsan.safety()

while True:
  pygame.event.get()

  throttle = max(0, -joystick.get_axis(4))
  rudder   = joystick.get_axis(0)
  elevator = joystick.get_axis(1)
  aileron  = joystick.get_axis(3)

  hubsan.control(throttle, rudder, elevator, aileron)
