import os, sys, pygame
from pygame.locals import *
from spritesheet import *
import map

pygame.init()
screen = pygame.display.set_mode((540,300), RESIZABLE)
pygame.mouse.set_visible(0)

'''def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', name)
        raise SystemExit
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()'''

class Background(pygame.sprite.Sprite):
    def __init__(self, image_file):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        #self.rect.left, self.rect.top = location

class Character(pygame.sprite.Sprite):
    def __init__(self, file_name, expression_count):
        pygame.sprite.Sprite.__init__(self)
        self.images = SpriteSheet(file_name).load_strip(pygame.Rect((0,0), map.SPRITE_OFFSETS),  expression_count, colorkey = -1)
        self.expression = 0 # Default
        
        self.rect = pygame.Rect(map.SPRITE_LOCATION_LEFT, map.SPRITE_OFFSETS)
        self.image = self.images[self.expression]
        
    def chg_expression(self, expression):
        self.expression = expression
        
    def update(self, expression):
        self.image = self.images[self.expression]
        

BackGround1 = Background('./Assets/Backgrounds/house_background.png')
clock = pygame.time.Clock()
dead = False
annabelle = Character(map.ANNABELLE_PATH, map.ANNABELLE_EXPRESSIONS)
all_sprites = pygame.sprite.Group()
all_sprites.add(annabelle)

while (dead == False):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            dead = True
    screen.fill([255, 255, 255])
    screen.blit(BackGround1.image, (0,0))
    all_sprites.draw(screen)

    pygame.display.update()
    clock.tick(60)
