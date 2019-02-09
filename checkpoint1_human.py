import os, sys, pygame
from pygame.locals import *
from spritesheet import *
import map

pygame.init()
screen = pygame.display.set_mode(map.SCREEN_SIZE, RESIZABLE)
pygame.mouse.set_visible(map.MOUSE_VIS)

class Background(pygame.surface.Surface):
    def __init__(self, image_file):
        pygame.surface.Surface.__init__(self, map.SCREEN_SIZE)
        self.image = pygame.image.load(image_file).convert()
        self.rect = self.image.get_rect()
        #self.rect.left, self.rect.top = location
        
class TextBox(pygame.surface.Surface):
    def __init__(self):
        self.image = pygame.image.load(map.TEXTBOX_PATH).convert()
        self.rect = pygame.Rect(map.TEXTBOX_RECT)
        self.image.set_colorkey(self.image.get_at((0,0)))
        

class Character(pygame.sprite.Sprite):
    def __init__(self, file_name, expression_count, offsets = None):
        pygame.sprite.Sprite.__init__(self)
        self.images = SpriteSheet(file_name).load_strip(pygame.Rect((0,0), map.SPRITE_OFFSETS),  expression_count, colorkey = -1)
        self.expression = 0 # Default
        
        self.rect = pygame.Rect(map.SPRITE_LOCATION_LEFT, map.SPRITE_OFFSETS)
        self.image = self.images[self.expression]
        
    def chg_expression(self, expression):
        self.expression = expression
        
    def update(self, expression):
        self.image = self.images[self.expression]
        







BackGround1 = Background(map.BACKGROUND_HOUSE)
clock = pygame.time.Clock()
dead = False
all_sprites = pygame.sprite.Group()
annabelle = Character(map.ANNABELLE_PATH, map.ANNABELLE_EXPRESSIONS)
textbox = TextBox()
all_sprites.add(annabelle)

while (dead == False):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            dead = True
    screen.fill([255, 255, 255])
    screen.blit(BackGround1.image, (0,0))
    all_sprites.draw(screen)
    screen.blit(textbox.image, textbox.rect)

    pygame.display.update()
    clock.tick(60)
