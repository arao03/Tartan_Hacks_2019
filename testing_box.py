import os, sys, pygame
from pygame.locals import *
import map
from scene import *

pygame.init()
screen = pygame.display.set_mode(map.SCREEN_SIZE, RESIZABLE)
pygame.mouse.set_visible(map.MOUSE_VIS)

clock = pygame.time.Clock()
dead = False

scene0 = Scene()

while (dead == False):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            dead = True
    
    scene0.draw(screen)

    pygame.display.update()
    clock.tick(60)
