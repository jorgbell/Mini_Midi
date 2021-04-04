# creacion de una ventana de pygame
import pygame
from pygame.locals import *

WIDTH = 64
HEIGHT = 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Theremin")

#...

# obtencion de la posicion del raton
for event in pygame.event.get():
    if event.type == pygame.MOUSEMOTION:
        mouseX, mouseY = event.pos

pygame.quit()