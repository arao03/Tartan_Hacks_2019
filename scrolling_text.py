import pygame, time
pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

font = pygame.font.Font(None, 25)

# raise the USEREVENT every 1000ms
pygame.time.set_timer(pygame.USEREVENT, 300)

# generate a generator that scrolls through the letters
# given a string foo, it will return
# f
# fo
# foo
def text_generator(text):
    tmp = ''
    for letter in text:
        tmp += letter
        # don't pause for spaces
        if letter != ' ':
            yield tmp

# a simple class that uses the generator
# and can tell if it is done
class DynamicText(object):
    def __init__(self, font, text, pos, autoreset=False):
        self.done = False
        self.font = font
        self.text = text
        self._gen = text_generator(self.text)
        self.pos = pos
        self.autoreset = autoreset
        self.update()

    def reset(self):
        self._gen = text_generator(self.text)
        self.done = False
        self.update()

    def update(self):
        if not self.done:
            try: self.rendered = self.font.render(next(self._gen), True, (255, 255, 255))
            except StopIteration:
                self.done = True
                if self.autoreset: self.reset()

    def draw(self, screen):
        screen.blit(self.rendered, self.pos)

def parse_(filename):
    lines = []
    script = open(filename,"r")
    for l in script:
        lines.append(DynamicText(font,l.rstrip(),(25,250), autoreset=False))
    return lines

messagenumber = 0
def parse_script(lines,event,messagenumber):
    #pauseflag = 0
    if event.type == pygame.USEREVENT: lines[messagenumber].update()
    if lines[messagenumber].done == True:
            #if pauseflag == 0:
         time.sleep(1.5)
                #pauseflag = 1
         messagenumber += 1
    lines[messagenumber].draw(screen)
    return messagenumber

