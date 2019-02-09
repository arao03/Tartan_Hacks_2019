import os, sys, pygame
from pygame.locals import *
import map

pygame.init()
screen = pygame.display.set_mode(map.SCREEN_SIZE, RESIZABLE)
pygame.mouse.set_visible(map.MOUSE_VIS)

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
        #self.rect.left, self.rect.top = location
        
class TextBox(pygame.surface.Surface):
    def __init__(self):
        self.image = pygame.image.load(map.TEXTBOX_PATH).convert()
        self.rect = pygame.Rect(map.TEXTBOX_RECT)
        self.image.set_colorkey(self.image.get_at((0,0)))
        

class Character(pygame.sprite.Sprite):
    def __init__(self, file_name, expression_count, offsets = None):
        pygame.sprite.Sprite.__init__(self)
        self.images = SpriteSheet(file_name).load_strip(pygame.Rect((0,0), map.SPRITE_OFFSETS),  expression_count, colorkey = -1)
        self.expression = 0 # Default
        
        self.rect = pygame.Rect(map.SPRITE_LOCATION_LEFT, map.SPRITE_OFFSETS)
        self.image = self.images[self.expression]
        
    def chg_expression(self, expression):
        self.expression = expression
        
    def update(self, expression):
        self.image = self.images[self.expression]
        
        
background_dict = {"city": Background(map.BACKGROUND_CITY),
                   "house": Background(map.BACKGROUND_HOUSE),
                   "forge": Background(map.BACKGROUND_FORGE),
                   "school": Background(map.BACKGROUND_SCHOOL)}

character_dict = {"annabelle": Character(map.ANNABELLE_PATH, map.ANNABELLE_EXPRESSIONS),
                  "kaylin": Character(map.KAYLIN_PATH, map.KAYLIN_EXPRESSIONS),
                  "forvik": Character(map.FORVIK_PATH, map.FORVIK_EXPRESSIONS),
                  "elves": Character(map.ELF_PATH, 2),
                  "humans": Character(map.HUMAN_PATH, 2)}

textbox = TextBox()

class Scene(object):
    def __init__(self, background = None, character = None, expression = 0):        
        
        # Set the background for the scene.
        if background is not None:
            self.background = background_dict[background]
        else:
            self.background = background_dict["city"]
            
        # Set the character for the scene.
        if character is not None:
            self.character = character_dict[character]
            self.character.chg_expression(expression)
        else:
            self.character = None
            
            
    def draw(self, screen):
        all_sprites = pygame.sprite.Group()
        if self.character is not None:
            all_sprites.add(self.character)
        
        screen.fill([255, 255, 255])
        screen.blit(self.background.image, (0,0))
        all_sprites.draw(screen)
        screen.blit(textbox.image, textbox.rect)

        pygame.display.update()