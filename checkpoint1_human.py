import os, sys, pygame
from pygame.locals import *

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

class Human(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        sheet = pygame.image.load('./Assets/Sprites/annabelleexpsheet.png')
        self.image = 
        self.rect = [0,0]

BackGround1 = Background('./Assets/Backgrounds/house_background.png')
clock = pygame.time.Clock()
dead = False
annabelle = Human()
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
