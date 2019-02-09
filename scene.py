import os, sys, pygame
from pygame.locals import *
from userinput import *
import map
from scrolling_text import *
from operator import pos
from tts_basic import *

def initData(data):
    data.gameOver = False
    data.imageLibrary = {}
    data.soundLibrary = {}
    data.buttons = set()
    data.gametime = 0
    data.channel_speech = pygame.mixer.Channel(1)
    data.channel_speech.set_volume(1)
    
class Data(object): pass
    # Initialize an all-purpose data instance for the model
data = Data()
initData(data)

def posSwitch(argument):
    switcher = {
            0: pygame.Rect(map.SPRITE_LOCATION_LEFT, map.SPRITE_OFFSETS),
            1: pygame.Rect(map.SPRITE_LOCATION_RIGHT, map.SPRITE_OFFSETS),
            2: pygame.Rect(map.SPRITE_LOCATION_CENTER, map.SPRITE_OFFSETS),
            3: pygame.Rect(map.SPRITE_LOCATION_RIGHT2, map.SPRITE_OFFSETS)
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
        
        try: sound = pygame.mixer.Sound(filePath)
        except (error, message):
            pass
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

textbox = TextBox()

class Title(object):
    def __init__(self):
        self.background = background_dict["city"]
    
    def draw(self):
        screen.fill([255, 255, 255])
        screen.blit(self.background.image, (0,0))
        self.sprites.draw(screen)

        pygame.display.update()

class Scene(object):
    def __init__(self, background = None, character = None, text = None, audio = -1, transitions = None):
        self.id = id
        self.sprites = pygame.sprite.Group()
        self.messagenumber = 0
        self.audio = audio
        
        # Set transitions.
        if transitions is not None:
            self.transitions = transitions
        else:
            self.transitions = ["hintro", "eintro", "dintro"]
        # Set the text for the scene.
        if text is not None:
            self.text = script_dict[text]
        else:
            self.text = script_dict["open"]
        # Set the background for the scene.
        if background is not None:
            self.background = background_dict[background]
        else:
            self.background = background_dict["city"]
        # Set the character for the scene.
        if isinstance(character, list):
            for char in character:
                chartmp = character_dict[char]
                self.sprites.add(chartmp)
        else:
            for char in ["human-1l", "dwarf-0c", "elf-0r"]: # Default chars
                chartmp = character_dict[char]
                self.sprites.add(chartmp)
                
    def startScene(self):
        if self.audio == -1:
            self.playSpeech(audio_dict["open"], data.channel_speech, data.soundLibrary)
        elif self.audio is not None:
            if isinstance(audio_dict[self.audio], list):
                for aud in audio_dict[self.audio]:
                    self.queueSpeech(aud, data.channel_speech, data.soundLibrary)
            else:
                self.playSpeech(audio_dict[self.audio], data.channel_speech, data.soundLibrary)
    
    def goLeft(self):
        if len(self.transitions) > 0:
            self.stopPlayback(data.channel_speech)
            return (scene_dict[self.transitions[0]], True)
        else:
            print ("No left path")
            return (self, False)
    
    def goRight(self):
        if len(self.transitions) > 1:
            self.stopPlayback(data.channel_speech)
            return (scene_dict[self.transitions[1]], True)
        else:
            print ("No right path")
            return (self, False)
    
    def goCenter(self):
        if len(self.transitions) > 2:
            self.stopPlayback(data.channel_speech)
            return (scene_dict[self.transitions[2]], True)
        else:
            print ("Please choose left or right")
            return (self, False)
        
    def goTransition(self):
        if len(self.transitions) == 1:
            return (scene_dict[self.transitions[0]], True)
        else:
            return (self, False)
        
    def draw(self, screen, event, gametime):
        screen.fill([255, 255, 255])
        screen.blit(self.background.image, (0,0))
        self.sprites.draw(screen)
        screen.blit(textbox.image, textbox.rect)
        tempMessageNumber = parse_script(self.text, event, self.messagenumber, gametime)
        if tempMessageNumber:
            self.messagenumber = tempMessageNumber

        pygame.display.update()

    def playSpeech(self, path, channel, library):
        playSound(path, channel, library)
        
    def queueSpeech(self, path, channel, library):
        channel.queue(getSound(path, library))                         

    def stopPlayback(self, channel):
        stopSound(channel)
        
################################################### SCENE CREATION ######################################################
        
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
                  "elf-0r": Character(map.ELF_PATH, 2, 1, 0, True),
                  "elf-0r2": Character(map.ELF_PATH, 2, 3, 0, True),
                  "elf-1r": Character(map.ELF_PATH, 2, 1, 1),
                  "elf-0l": Character(map.ELF_PATH, 2, 0, 0),
                  "elf-1l": Character(map.ELF_PATH, 2, 0, 1, True),
                  "human-0r": Character(map.HUMAN_PATH, 2, 1, 0, True),
                  "human-0r2": Character(map.HUMAN_PATH, 2, 3, 0),
                  "human-1r": Character(map.HUMAN_PATH, 2, 1, 1),
                  "human-0l": Character(map.HUMAN_PATH, 2, 0, 0),
                  "human-1l": Character(map.HUMAN_PATH, 2, 0, 1, True),
                  "dwarf-0r": Character(map.DWARF_PATH, 1, 1, 0),
                  "dwarf-0l": Character(map.DWARF_PATH, 2, 0, 0, True),
                  "dwarf-0c": Character(map.DWARF_PATH, 2, 2, 0, True)}
        
script_dict = {"open": parse_(map.OPENING_SCRIPT),
               "hintro": parse_(map.HUMAN_INTRO),
               "heduintro": parse_(map.HUMAN_ED_INTRO),
               "hsit1elf": parse_(map.HUMAN_SIT1_ELF),
               "hsit1elft1": parse_(map.HUMAN_SIT1_ELF_TRANS1),
               "hsit1elft2": parse_(map.HUMAN_SIT1_ELF_TRANS2),
               "hsit2elf": parse_(map.HUMAN_SIT2_ELF),
               "hsit2human": parse_(map.HUMAN_SIT2_HUMAN),
               "hsit1human": parse_(map.HUMAN_SIT1_HUMAN),
               "htradeintro": parse_(map.HUMAN_TR_INTRO),
               "hteam1dwarf": parse_(map.HUMAN_TEAM1_DWARF),
               "hteam1dwarft1": parse_(map.HUMAN_TEAM1_DWARF_TRANS1),
               "hteam1dwarft2": parse_(map.HUMAN_TEAM1_DWARF_TRANS2),
               "hteam2dwarf": parse_(map.HUMAN_TEAM2_DWARF),
               "hteam2human": parse_(map.HUMAN_TEAM2_HUMAN),
               "hteam1human": parse_(map.HUMAN_TEAM1_HUMAN),
               "eintro": parse_(map.ELF_INTRO),
               "etrintro": parse_(map.ELF_TRAD_INTRO),
               "esit1human": parse_(map.ELF_SIT1_HUMAN),
               "esit1humant1": parse_(map.ELF_SIT1_HUMAN_TRANS1),
               "esit1humant2": parse_(map.ELF_SIT1_HUMAN_TRANS2),
               "esit2human": parse_(map.ELF_SIT2_HUMAN),
               "esit2elf": parse_(map.ELF_SIT2_ELF),
               "esit1elf": parse_(map.ELF_SIT1_ELF),
               "etutintro": parse_(map.ELF_TUT_INTRO),
               "etutintrot": parse_(map.ELF_TUT_INTRO_TRANS),
               "esmile1dwarf": parse_(map.ELF_SMILE1_DWARF),
               "esmile2dwarf": parse_(map.ELF_SMILE2_DWARF),
               "esmile2elf": parse_(map.ELF_SMILE2_ELF),
               "esmile1elf": parse_(map.ELF_SMILE1_ELF),
               "dintro": parse_(map.DWARF_INTRO),
               "dschoolintro": parse_(map.DWARF_SCHOOL_YOU),
               "dsit1dwarf": parse_(map.DWARF_SIT1_DWARF),
               "dsit1human": parse_(map.DWARF_SIT1_HUMAN),
               "dsit1humant1": parse_(map.DWARF_SIT1_HUMAN_TRANS1),
               "dsit1humant2": parse_(map.DWARF_SIT1_HUMAN_TRANS2),
               "dsit2dwarf": parse_(map.DWARF_SIT2_DWARF),
               "dsit2human": parse_(map.DWARF_SIT2_HUMAN),
               "dschoolbro": parse_(map.DWARF_SCHOOL_BRO),
               "dadvintro": parse_(map.DWARF_ADV_INTRO),
               "dbladeyes": parse_(map.DWARF_BLADE_YES),
               "dbladeno": parse_(map.DWARF_BLADE_NO)
               }
    
audio_dict = {"open": "./Assets/Speech/audio_welcome.wav",
              "hintro": "./Assets/Speech/audio_human_intro.wav",
              "heduintro": "./Assets/Speech/audio_human_education.wav",
              "hsit1elf": ["./Assets/Speech/audio_human_education_elf_1.wav", "./name.wav", "./Assets/Speech/audio_human_education_elf_2.wav"],
              "hsit2elf": "./Assets/Speech/audio_human_education_elf_Kaylin.wav",
              "hsit1human": "./Assets/Speech/audio_human_education_humans.wav",
              "hsit2human": "./Assets/Speech/audio_human_education_elf_human.wav",
              "htradeintro": "./Assets/Speech/audio_human_trade.wav",
              "hteam1dwarf": ["./Assets/Speech/audio_human_trade_dwarf_1.wav", "./name.wav", "./Assets/Speech/audio_human_trade_dwarf_2.wav"],
              "hteam2dwarf": "./Assets/Speech/audio_human_trade_dwarf_Fovik.wav",
              "hteam2human": "./Assets/Speech/audio_human_trade_dwarf_humans.wav",
               "hteam1human": "./Assets/Speech/audio_human_trade_human.wav",
               "eintro": "./Assets/Speech/audio_elf_intro.wav",
               "etrintro": "./Assets/Speech/audio_elf_TE.wav",
               "esit1human": ["./Assets/Speech/audio_elf_TE_human_1.wav", "./name.wav", "./Assets/Speech/audio_elf_TE_human_2.wav"],
               "esit2human": "./Assets/Speech/audio_elf_TE_human_Annabelle.wav",
               "esit2elf": "./Assets/Speech/audio_elf_TE_human_elf.wav",
               "esit1elf": "./Assets/Speech/audio_elf_TE_elves.wav",
               "etutintro": "./Assets/Speech/audio_elf_tutor.wav",
               "esmile1dwarf": "./Assets/Speech/audio_elf_tutor_smile.wav",
               "esmile2dwarf": "./Assets/Speech/audio_elf_tutor_smile_defend.wav",
               "esmile2elf": "./Assets/Speech/audio_elf_tutor_smile_silent.wav",
               "esmile1elf": "./Assets/Speech/audio_elf_tutor_turn.wav",
               "dintro": "./Assets/Speech/audio_dwarf_intro.wav",
               "dschoolintro": "./Assets/Speech/audio_dwarf_education.wav",
               "dsit1dwarf": "./Assets/Speech/audio_dwarf_educaion_dwarves.wav",
               "dsit1human": "./Assets/Speech/audio_dwarf_education_human_1.wav",
               "dsit2dwarf": "./Assets/Speech/audio_dwarf_education_human_dwarf.wav",
               "dsit2human": "./Assets/Speech/audio_dwarf_education_human_Annabelle.wav",
               "dschoolbro": "./Assets/Speech/audio_dwarf_brother.wav",
               "dadvintro": "./Assets/Speech/audio_dwarf_brother_adventure_1.wav",
               "dbladeyes": "./Assets/Speech/audio_dwarf_brother_adventure_blade.wav",
               "dbladeno": "./Assets/Speech/audio_dwarf_brother_adventure_silent.wav"
            }
        
scene_dict = {"open": Scene(),
              "hintro": Scene("city", ["human-1l"], "hintro", "hintro", ["heduintro", "htradeintro"]),
              "heduintro": Scene("school", ["kaylin-l", "human-0r2", "human-1r"], "heduintro", "heduintro", ["hsit1elf", "hsit1human"]),
              "hsit1elf": Scene("school", ["kaylin-l"], "hsit1elf", "hsit1elf", ["hsit1elft1"]),
              "hsit1elft1": Scene("school", ["human-0r2", "human-1r"], "hsit1elft1", None, ["hsit1elft2"]),
              "hsit1elft2": Scene("school", ["kaylin-l", "human-1r"], "hsit1elft2", None, ["hsit2elf", "hsit2human"]),
              "hsit2elf": Scene("school", ["kaylin-l"], "hsit2elf", "hsit2elf", []),
              "hsit1human": Scene("school", ["human-0r2", "human-1r"], "hsit1human", "hsit1human", []),
              "hsit2human": Scene("school", ["human-0r2", "human-1r"], "hsit2human", "hsit2human", []),
              "htradeintro": Scene("forge", ["forvik-l", "human-1r"], "htradeintro", "htradeintro", ["hteam1dwarf"]),
              "hteam1dwarf": Scene("forge", ["forvik-l"], "hteam1dwarf", "hteam1dwarf", ["hteam1dwarft1"]),
              "hteam1dwarft1": Scene("forge", ["forvik-l"], "hteam1dwarft1", None, ["hteam1dwarft2"]),
              "hteam1dwarft2": Scene("forge", ["forvik-l", "human-1r"], "hteam1dwarft2", None, ["hteam2dwarf"]),
              "hteam2dwarf": Scene("house", ["forvik-l"], "hteam2dwarf", "hteam2dwarf", []),
              "hteam2human": Scene("house", [], "hteam2human", "hteam2human", []),
              "hteam1human": Scene("house", [], "hteam1human", "hteam1human", []),
              "eintro": Scene("city", ["elf-1l"], "eintro", "eintro", ["etrintro", "etutintro"]),
              "etrintro": Scene("school", ["annabelle-l", "elf-1r"], "etrintro", "etrintro", ["esit1human", "esit1elf"]),
              "esit1human": Scene("school", ["annabelle-l"], "esit1human", "esit1human", ["esit1humant1"]),
              "esit1humant1": Scene("school", ["human-0l", "human-1r"], "esit1humant1", None, ["esit1humant2"]),
              "esit1humant2": Scene("school", ["annabelle-l", "elf-0r"], "esit1humant2", None, ["esit2human", "esit2elf"]),
              "esit2human": Scene("house", ["annabelle-l"], "esit2human", "esit@human", []),
              "esit2elf": Scene("house", [], "esit2elf", "esit2elf", []),
              "esit1elf": Scene("house", [], "esit1elf", "esit1elf", []),
              "etutintro": Scene("house", ["elf-0l"], "etutintro", "etutintro", ["etutintrot"]),
              "etutintrot": Scene("forge", ["forvik-l"], "etutintrot", None, ["esmile1dwarf", "esmile1elf"]),
              "esmile1dwarf": Scene("forge", ["forvik-l", "elf-0r"], "esmile1dwarf", "esmile1dwarf", ["esmile2dwarf", "esmile2elf"]),
              "esmile2dwarf": Scene("house", ["elf-0l", "forvik-r"], "esmile2dwarf", "esmile2dwarf", []),
              "esmile2elf": Scene("house", ["elf-0l"], "esmile2elf", "esmile2elf", []),
              "esmile1elf": Scene("house", [], "esmile1elf", "esmile1elf", []),
              "dintro": Scene("city", ["forvik-l"], "dintro", "dintro", ["dschoolintro", "dschoolbro"]),
              "dschoolintro": Scene("school", ["annabelle-l", "dwarf-0r"], "dschoolintro", "dschoolintro", ["dsit1human", "dsit1dwarf"]),
              "dsit1human": Scene("school", ["annabelle-l"], "dsit1human", "dsit1human", ["dsit1humant1"]),
              "dsit1humant1": Scene("school", ["dwarf-0l", "dwarf-0r"], "dsit1humant1", None, ["dsit1humant2"]),
              "dsit1humant2": Scene("school", ["annabelle-l", "dwarf-0r"], "dsit1humant2", None, ["dsit2human", "dsit2dwarf"]),
              "dsit2human": Scene("forge", ["annabelle-l"], "dsit2human", "dsit2human", []),
              "dsit2dwarf": Scene("forge", [], "dsit2dwarf", "dsit2dwarf", []),
              "dsit1dwarf": Scene("forge", [], "dsit1dwarf", "dsit1dwarf", []),
              "dschoolbro": Scene("forge", [], "dschoolbro", "dschoolbro", ["dschoolintro", "dadvintro"]),
              "dadvintro": Scene("forge", ["kaylin-l"], "dadvintro", "dadvintro", ["dbladeyes", "dbladeno"]),
              "dbladeyes": Scene("forge", ["kaylin-l"], "dbladeyes", "dbladeyes", []),
              "dbladeno": Scene("forge", [], "dbladeno", "dbladeno", [])
              }
