'''
TartanHacks 2019
imcmahon, lkipp, ananyara, asteiner
'''

# This file defines what a scene is, which carries information about everything that is shown on screen #

class Scene(object):
    def __init__(self, sceneInfo):
        # sceneInfo should be a dictionary that carries all the asset info for the scene
        # This includes the background picture, characters, text, and other stuff
        self.sceneInfo = sceneInfo


