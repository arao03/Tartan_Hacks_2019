import os, sys, pygame
from pygame.locals import *
from userinput import *
import map
from scrolling_text import *
from operator import pos

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
        image = pygame.image.load(filePath)
        library[path] = image
    return image

class SpriteSheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
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
        self.image = pygame.image.load(image_file).convert()
        self.rect = self.image.get_rect()
        
class TextBox(pygame.surface.Surface):
    def __init__(self):
        self.image = pygame.image.load(map.TEXTBOX_PATH).convert()
        self.rect = pygame.Rect(map.TEXTBOX_RECT)
        self.image.set_colorkey(self.image.get_at((0,0)))

class Character(pygame.sprite.Sprite):
    def __init__(self, file_name, expression_count, position = 0, expression = 0):
        pygame.sprite.Sprite.__init__(self)
        self.val_dict = {"file_name": file_name,
                         "expression_count": expression_count,
                         "position": position,
                         "expression": expression}
        
        self.images = SpriteSheet(file_name).load_strip(pygame.Rect((0,0), map.SPRITE_OFFSETS),  expression_count, colorkey = (255,255,255))
            
        self.rect = posSwitch(self.val_dict["position"])
        self.image = self.images[self.val_dict["position"]]
        
    def updateCharacter(self, key, arguement):
        self.val_dict[key] = arguement
        self.update()
        
    def update(self):
        self.image = self.images[self.val_dict["expression"]]
        self.rect = posSwitch(self.val_dict["position"])
        
        
background_dict = {"city": Background(map.BACKGROUND_CITY),
                   "house": Background(map.BACKGROUND_HOUSE),
                   "forge": Background(map.BACKGROUND_FORGE),
                   "school": Background(map.BACKGROUND_SCHOOL)}

character_dict = {"annabelle": Character(map.ANNABELLE_PATH, map.ANNABELLE_EXPRESSIONS),
                  "kaylin": Character(map.KAYLIN_PATH, map.KAYLIN_EXPRESSIONS),
                  "forvik": Character(map.FORVIK_PATH, map.FORVIK_EXPRESSIONS),
                  "elf": Character(map.ELF_PATH, 2),
                  "human": Character(map.HUMAN_PATH, 2)}

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
               "elfintro": parse_(map.ELF_INTRO),
               "elftrintro": parse_(map.ELF_TRAD_INTRO)
               }

textbox = TextBox()

class Scene(object):
    def __init__(self, background = None, character = None, text = None, buttons= None):        
        self.id = id
        self.sprites = pygame.sprite.Group()
        self.messagenumber = 0
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
            for (char, exp, pos) in character:
                chartmp = character_dict[char]
                chartmp.updateCharacter("expression", exp)
                chartmp.updateCharacter("position", pos)
                self.sprites.add(chartmp)
        else:
            print "Please provide characters as a list [left, right, center]"
            raise SystemError
        
        # Set the buttons.
        if isinstance(buttons, list):
            self.buttons = buttons
        elif isinstance(character, list):
            print "Please provide buttons for your character."
            raise SystemError

        
    def draw(self, screen, event, gametime):
        screen.fill([255, 255, 255])
        screen.blit(self.background.image, (0,0))
        self.sprites.draw(screen)
        screen.blit(textbox.image, textbox.rect)

        self.messagenumber = parse_script(self.text, event, self.messagenumber, gametime)

        pygame.display.update()
        
scene_dict = {"open": Scene(background="city", character=[("human", 0, 0), ("elf", 0, 1), ("elf", 1, 2)], text="open", buttons=[button_dict[0], button_dict[1], button_dict[2]]),
              "0": Scene("city", [("human", 1, 0)], "hintro", [button_dict[3]]),
              "1": Scene("city", [("elf", 1, 2)], "elfintro", [button_dict[3]]), # placeholder
              "2": Scene("city", [("elf", 0, 1)], "hintro", [button_dict[3]]), # placeholder
              "3": Scene("school", [("kaylin", 0, 0), ("human", 1, 1)], "heduintro", [button_dict[0]])}