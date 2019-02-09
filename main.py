'''
TartanHacks2019
imcmahon, lkipp, ananyara, asteiner
'''


import pygame
from scene import *


def initData(data):
    data.gameOver = False
    data.imageLibrary = {}


def main():
    pygame.init()
    pygame.font.init()

    class Data(object): pass
    # Initialize an all-purpose data instance for the model
    data = Data()
    initData(data)
    size = map.SCREEN_SIZE
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(map.GAME_TITLE)
    time = pygame.time.Clock()
    scene = Scene()
    pygame.mixer.music.load("./Assets/Music/menu.ogg")  # This is where to look for music playing
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(.3)

    while not data.gameOver:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data.gameOver = True

        screen.fill((255, 255, 255))
        scene.draw(screen)
        
        time.tick(60)
        pygame.display.flip()
    pygame.quit()
    print("hell yeah hit that button")


if __name__ == "__main__":
    main()
