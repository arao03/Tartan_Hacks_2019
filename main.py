'''
TartanHacks2019
imcmahon, lkipp, ananyara, asteiner
'''


import pygame
from scene import *
from userinput import *


def initData(data):
    data.gameOver = False
    data.imageLibrary = {}
    data.soundLibrary = {}
    data.buttons = set()
    data.gametime = 0

def main():
    pygame.init()
    startScene = True;

    class Data(object): pass
    # Initialize an all-purpose data instance for the model
    data = Data()
    initData(data)
    size = map.SCREEN_SIZE
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(map.GAME_TITLE)
    time = pygame.time.Clock()
    scene = scene_dict["open"]
    data.channel_music = pygame.mixer.Channel(0)
    data.channel_music.set_volume(1)
    playSound(map.MUSIC_PATH, data.channel_music, data.soundLibrary)  # This is where to look for music playing
    #playSound(map.WELCOME_AUDIO, data.channel_speech, data.soundLibrary)

    while not data.gameOver:        
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data.gameOver = True
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    (scene, startScene) = scene.goLeft()
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    (scene, startScene) = scene.goRight()
                elif keys[pygame.K_w] or keys[pygame.K_DOWN]:
                    (scene, startScene) = scene.goCenter()
                elif keys[pygame.K_SPACE]:
                    (scene, startScene) = scene.goTransition()
                        
        screen.fill((255, 255, 255))
        scene.draw(screen, event, data.gametime)
        
        if startScene: 
            scene.startScene()
            startScene = False
        
        time.tick(60)
        data.gametime = (data.gametime + 1) % (2**12)
        pygame.display.update()
        pygame.display.flip()
        pygame.event.pump()

    pygame.quit()


if __name__ == "__main__":
    main()
