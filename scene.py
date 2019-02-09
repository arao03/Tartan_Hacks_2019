import os, sys, pygame
from pygame.locals import *
from userinput import *
import map
from scrolling_text import *
from operator import pos

def initData(data):
    data.gameOver = False
    data.imageLibrary = {}
    data.soundLibrary = {}
    data.buttons = set()
    data.gametime = 0
    
class Data(object): pass
    # Initialize an all-purpose data instance for the model
data = Data()
initData(data)

def posSwitch(argument):
    switcher = {
            0: pygame.Rect(map.SPRITE_LOCATION_LEFT, map.SPRITE_OFFSETS),
            1: pygame.Rect(map.SPRITE_LOCATION_RIGHT, map.SPRITE_OFFSETS),
            2: pygame.Rect(map.SPRITE_LOCATION_CENTER, map.SPRITE_OFFSETS)
        }
    return switcher[argument]

def getImg(path, library):
    # https://nerdparadise.com/programming/pygame/part2

    # When called, checks global variable imgLib for the image. If it has not
    # already been loaded, then loads image.
    image = library.get(path)
    if image == None:
        filePath = path.replace("/", os.sep).replace("\\", os.sep)
        image = pygame.image.load(filePath).convert()
        library[path] = image
    return image

def getSound(path, library):
    sound = library.get(path)
    if sound == None:
        filePath = path.replace("/", os.sep).replace("\\", os.sep)
        sound = pygame.mixer.Sound(filePath)
        library[path] = sound
    return sound

def playSound(path, channel, library):
    channel.play(getSound(path, library))

def stopSound(channel):
    channel.stop()

class SpriteSheet(object):
    def __init__(self, filename):
        try:
            self.sheet = getImg(filename, data.imageLibrary)
        except (pygame.error, message):
            print ('Unable to load spritesheet image:', filename)
            raise (SystemExit, message)
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class SpriteStripAnim(object):
    """sprite strip animator
    
    This class provides an iterator (iter() and next() methods), and a
    __add__() method for joining strips which comes in handy when a
    strip wraps to the next row.
    """
    def __init__(self, filename, rect, count, colorkey=None, loop=False, frames=1):
        """construct a SpriteStripAnim
        
        filename, rect, count, and colorkey are the same arguments used
        by spritesheet.load_strip.
        
        loop is a boolean that, when True, causes the next() method to
        loop. If False, the terminal case raises StopIteration.
        
        frames is the number of ticks to return the same image before
        the iterator advances to the next image.
        """
        self.filename = filename
        ss = spritesheet.spritesheet(filename)
        self.images = ss.load_strip(rect, count, colorkey)
        self.i = 0
        self.loop = loop
        self.frames = frames
        self.f = frames
    def iter(self):
        self.i = 0
        self.f = self.frames
        return self
    def next(self):
        if self.i >= len(self.images):
            if not self.loop:
                raise StopIteration
            else:
                self.i = 0
        image = self.images[self.i]
        self.f -= 1
        if self.f == 0:
            self.i += 1
            self.f = self.frames
        return image
    def __add__(self, ss):
        self.images.extend(ss.images)
        return self

class Background(pygame.surface.Surface):
    def __init__(self, image_file):
        pygame.surface.Surface.__init__(self, map.SCREEN_SIZE)
        self.image = getImg(image_file, data.imageLibrary)
        self.rect = self.image.get_rect()
        
class TextBox(pygame.surface.Surface):
    def __init__(self):
        self.image = getImg(map.TEXTBOX_PATH, data.imageLibrary)
        self.rect = pygame.Rect(map.TEXTBOX_RECT)
        self.image.set_colorkey(self.image.get_at((0,0)))

class Character(pygame.sprite.Sprite):
    def __init__(self, file_name, expression_count, position = 0, expression = 0, flipped = False):
        pygame.sprite.Sprite.__init__(self)
        self.val_dict = {"position": position,
                         "expression": expression}
        
        self.images = SpriteSheet(file_name).load_strip(pygame.Rect((0,0), map.SPRITE_OFFSETS),  expression_count, colorkey = (255,255,255))
            
        self.rect = posSwitch(self.val_dict["position"])
        if flipped:
            self.image = pygame.transform.flip(self.images[self.val_dict["expression"]], True, False)
        else:
            self.image = self.images[self.val_dict["expression"]]
        
    def get_dict(self):
        return self.val_dict
    
    def set_dict(self, key, argument):
        self.val_dict[key] = argument
        self.update()
        
    def update(self):
        self.rect = posSwitch(self.val_dict["position"])
        self.image = self.images[self.val_dict["expression"]]
        
    dict = property(get_dict, set_dict)

class Icon(pygame.sprite.Sprite):
    def __init__(self, file_name, position):
        self.image = getImg(file_name, data.imageLibrary)
        self.rect = posSwitch(position)
        
background_dict = {"city": Background(map.BACKGROUND_CITY),
                   "house": Background(map.BACKGROUND_HOUSE),
                   "forge": Background(map.BACKGROUND_FORGE),
                   "school": Background(map.BACKGROUND_SCHOOL)}

character_dict = {"annabelle-l": Character(map.ANNABELLE_PATH, map.ANNABELLE_EXPRESSIONS, 0, 0),
                  "kaylin-l": Character(map.KAYLIN_PATH, map.KAYLIN_EXPRESSIONS, 0, 0),
                  "forvik-l": Character(map.FORVIK_PATH, map.FORVIK_EXPRESSIONS, 0, 0),
                  "annabelle-r": Character(map.ANNABELLE_PATH, map.ANNABELLE_EXPRESSIONS, 1, 0, True),
                  "kaylin-r": Character(map.KAYLIN_PATH, map.KAYLIN_EXPRESSIONS, 1, 0, True),
                  "forvik-r": Character(map.FORVIK_PATH, map.FORVIK_EXPRESSIONS, 1, 0, True),
                  "elf-0r": Character(map.ELF_PATH, 2, 0, 0),
                  "elf-1r": Character(map.ELF_PATH, 2, 0, 1, True),
                  "elf-0l": Character(map.ELF_PATH, 2, 1, 0, True),
                  "elf-1l": Character(map.ELF_PATH, 2, 1, 1),
                  "human-0r": Character(map.HUMAN_PATH, 2, 0, 0),
                  "human-1r": Character(map.HUMAN_PATH, 2, 0, 1, True),
                  "human-0l": Character(map.HUMAN_PATH, 2, 1, 0, True),
                  "human-1l": Character(map.HUMAN_PATH, 2, 1, 1)}

script_dict = {"open": parse_(map.OPENING_SCRIPT),
               "hintro": parse_(map.HUMAN_INTRO),
               "heduintro": parse_(map.HUMAN_ED_INTRO),
               "hsit1elf": parse_(map.HUMAN_SIT1_ELF),
               "hsit2elf": parse_(map.HUMAN_SIT2_ELF),
               "hsit2human": parse_(map.HUMAN_SIT2_HUMAN),
               "hsit1human": parse_(map.HUMAN_SIT1_HUMAN),
               "htradeintro": parse_(map.HUMAN_TR_INTRO),
               "hteam1dwarf": parse_(map.HUMAN_TEAM1_DWARF),
               "hteam2dwarf": parse_(map.HUMAN_TEAM2_DWARF),
               "hteam2human": parse_(map.HUMAN_TEAM2_HUMAN),
               "hteam1human": parse_(map.HUMAN_TEAM1_HUMAN),
               "eintro": parse_(map.ELF_INTRO),
               "etrintro": parse_(map.ELF_TRAD_INTRO),
               "esit1human": parse_(map.ELF_SIT1_HUMAN),
               "esit2human": parse_(map.ELF_SIT2_HUMAN),
               "esit2elf": parse_(map.ELF_SIT2_ELF),
               "esit1elf": parse_(map.ELF_SIT1_ELF),
               "etutintro": parse_(map.ELF_TUT_INTRO),
               "esmile1dwarf": parse_(map.ELF_SMILE1_DWARF),
               "esmile2dwarf": parse_(map.ELF_SMILE2_DWARF),
               "esmile2elf": parse_(map.ELF_SMILE2_ELF),
               "esmile1elf": parse_(map.ELF_SMILE1_ELF)
               }

textbox = TextBox()

class Scene(object):
    def __init__(self, background = None, character = None, text = None, audio = None, transitions = None):
        self.id = id
        self.sprites = pygame.sprite.Group()
        self.messagenumber = 0
        
        # Set transitions.
        if transitions is not None:
            self.transitions = transitions
        else:
            self.transitions = [0,1,2]
        # Set the text for the scene.
        if text is not None:
            self.text = script_dict[text]
        else:
            self.text = script_dict["open"]
        # Set the text for the scene.
        if audio is not None:
            self.audio = map.WELCOME_AUDIO
        else:
            self.audio = map.WELCOME_AUDIO
        # Set the background for the scene.
        if background is not None:
            self.background = background_dict[background]
        else:
            self.background = background_dict["city"]
        # Set the character for the scene.
        if character is not None:
            for (char, exp, pos) in character:
                chartmp = character_dict[char]
                chartmp.dict["expression"] = exp
                chartmp.dict["position"] = pos
                self.sprites.add(chartmp)
        else:
            for (char, exp, pos) in [("human-1r", 1, 0), ("elf-0l", 1, 2)]: # Default chars
                chartmp = character_dict[char]
                chartmp.dict["expression"] = exp
                chartmp.dict["position"] = pos
                self.sprites.add(chartmp)
    
    def goLeft(self):
        return scene_dict[self.transitions[0]]
    
    def goRight(self):
        return scene_dict[self.transitions[1]]
    
    def goCenter(self):
        if len(transitions > 2):
            return scene_dict[self.transitions[2]]
        else:
            print "Incorrect option"
            return self
        
        
    def draw(self, screen, event, gametime):
        screen.fill([255, 255, 255])
        screen.blit(self.background.image, (0,0))
        self.sprites.draw(screen)
        screen.blit(textbox.image, textbox.rect)

        self.messagenumber = parse_script(self.text, event, self.messagenumber, gametime)

        pygame.display.update()

    def playSpeech(self, path, channel, library):
        playSound(path, channel, library)

    def stopPlayback(self, channel):
        stopSound(channel)
        
scene_dict = {"open": Scene(),
              0: Scene("city", [("human-1r", 1, 0)], "hintro", [3]),
              1: Scene("city", [("elf-1l", 1, 2)], "eintro", [3]), # placeholder
              2: Scene("city", [("elf-1l", 0, 1)], "hintro", [3]), # placeholder
              3: Scene("school", [("kaylin-l", 0, 0), ("human-0l", 1, 1)], "heduintro", [0, 1])}
