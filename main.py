'''
TartanHacks2019
imcmahon, lkipp, ananyara, asteiner
'''


import pygame
from scene import *
from userinput import *
from tts_basic import *

def initData(data):
    data.gameOver = False
    data.imageLibrary = {}
    data.soundLibrary = {}
    data.buttons = set()
    data.gametime = 0
    data.playerName = input("What is your name?\n")


def main():
    pygame.init()
    startButton = Button(0, (195,210), (150, 60))
    startGame = True
    startedGame = False
    startScene = False

    class Data(object): pass
    # Initialize an all-purpose data instance for the model
    data = Data()
    initData(data)
    screen = pygame.display.set_mode(map.SCREEN_SIZE)
    pygame.display.set_caption(map.GAME_TITLE)
    time = pygame.time.Clock()
    title = Title()
    scene = scene_dict["open"]
    data.channel_music = pygame.mixer.Channel(0)
    data.channel_music.set_volume(.5)
    playSound(map.MUSIC_PATH, data.channel_music, data.soundLibrary)  # This is where to look for music playing
    #playSound(map.WELCOME_AUDIO, data.channel_speech, data.soundLibrary)
    
    
    
    
    while not data.gameOver:
        screen.fill((255, 255, 255))

        if not startedGame:
            title.draw()
            pygame.display.update()

        if startGame:
            subscription_key = "ba1a0f518f644cafb99630f0b734b42b"
            app = TextToSpeech(subscription_key,data.playerName)
            app.get_token()
            app.save_audio()
            startGame = False 
             
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data.gameOver = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if startButton.buttonPressed(event):
                    startScene = True
                    startedGame = True
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    (scene, startScene) = scene.goLeft()
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    (scene, startScene) = scene.goRight()
                elif keys[pygame.K_w] or keys[pygame.K_DOWN]:
                    (scene, startScene) = scene.goCenter()
                elif keys[pygame.K_SPACE]:
                    (scene, startScene) = scene.goTransition()
                elif keys[pygame.K_ESCAPE]:
                    data.gameOver = True
                    continue;

                
        if startScene: 
            scene.startScene()
            startScene = False
        if startedGame:
            scene.draw(screen, event, data.gametime)

        
        time.tick(60)
        data.gametime = (data.gametime + 1) % (2**12)
        pygame.display.flip()
        pygame.event.pump()

    pygame.quit()


if __name__ == "__main__":
    main()
