import pygame, time
pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

font = pygame.font.Font(None, 25)

# raise the USEREVENT every 1000ms
pygame.time.set_timer(pygame.USEREVENT, 100)

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
            try: self.rendered = self.font.render(next(self._gen), True, (0, 128, 0))
            except StopIteration:
                self.done = True
                if self.autoreset: self.reset()

    def draw(self, screen):
        screen.blit(self.rendered, self.pos)

messagefile = open("./Assests/textfiles/scene1.txt")

message1 = DynamicText(font, "A long time ago...", (200, 200), autoreset=False)
message2 = DynamicText(font, "there existed a...", (200, 200), autoreset=False)
messagenumber = 1
pauseflag = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: break
        if messagenumber == 1:
            if event.type == pygame.USEREVENT: message1.update()
        else:
            if event.type == pygame.USEREVENT: message2.update()
    else:
        screen.fill(pygame.color.Color('black'))
        if message1.done == True:
            if pauseflag == 0:
                pygame.time.delay(500)
                pauseflag = 1
            messagenumber = 2
        if messagenumber == 1:
            message1.draw(screen)
        else:
            message2.draw(screen)
        pygame.display.update()
        clock.tick(120)
        continue
    break
