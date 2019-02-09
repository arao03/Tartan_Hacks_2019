'''
TartanHacks 2019
imcmahon, lkipp, ananyara, asteiner
'''


class Button(object):
    def __init__(self, coordinates, size):
        # both coordinates and size are tuples
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.w = size[0]
        self.h = size[1]

    def buttonPressed(self, event):
        if (self.x < event.pos[0] < self.x + self.w) \
                and (self.y < event.pos[1] < self.y + self.h):
            return True
        else:
            return False

    def __hash__(self):
        return hash((self.x, self.y, self.h, self.w))

    def __eq__(self, other):
        return isinstance(other, Button) \
                and self.x == other.x and self.y == other.y  \
                and self.h == other.h and self.w == other.w
