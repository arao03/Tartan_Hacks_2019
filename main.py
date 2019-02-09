'''
TartanHacks2019
imcmahon, lkipp, ananyara, asteiner
'''


import pygame
from scene import *
from userinput import *


def changeScene(buttonid):
    return scene_dict[str(buttonid)]

def initData(data):
    data.gameOver = False
    data.imageLibrary = {}
    data.buttons = set()
    data.gametime = 0

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
    scene = scene_dict["open"]
    pygame.mixer.music.load(map.MUSIC_PATH)  # This is where to look for music playing
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(.3)

    while not data.gameOver:
        for key in pygame.key.get_pressed():
            if key == pygame.K_a:
                scene = scene.goLeft()
            elif key == pygame.K_d:
                scene = scene.goRight()
            elif key == pygame.K_w:
                scene = scene.gotCenter()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data.gameOver = True
            elif event.type == pygame.K_DOWN:
                if event.key == pygame.K_a:
                    scene = scene.goLeft()
                elif event.key == pygame.K_d:
                    scene = scene.goRight()
                elif event.key == pygame.K_w:
                    scene = scene.gotCenter()
                
        screen.fill((255, 255, 255))
        scene.draw(screen, event, data.gametime)
        
        time.tick(60)
        data.gametime = (data.gametime + 1) % 127
        pygame.display.update()
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
