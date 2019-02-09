'''
TartanHacks 2019
imcmahon, lkipp, ananyara, asteiner
'''
import map

class Button(object):
    def __init__(self, id, coordinates, size):
        # both coordinates and size are tuples
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.w = size[0]
        self.h = size[1]
        self.id = id

    def buttonPressed(self, event):
        if (self.x < event.pos[0] < self.x + self.w) \
                and (self.y < event.pos[1] < self.y + self.h):
            return True
        return False

    def __hash__(self):
        return hash((self.x, self.y, self.h, self.w))

    def __eq__(self, other):
        return isinstance(other, Button) \
                and self.x == other.x and self.y == other.y  \
                and self.h == other.h and self.w == other.w
                
                
button_dict = { 0: Button(0, map.SPRITE_LOCATION_LEFT, map.SPRITE_OFFSETS),
                1: Button(1, map.SPRITE_LOCATION_RIGHT, map.SPRITE_OFFSETS),
                2: Button(2, map.SPRITE_LOCATION_CENTER, map.SPRITE_OFFSETS),
                3: Button(3, map.SPRITE_LOCATION_LEFT, map.SPRITE_OFFSETS),
                4: Button(4, map.SPRITE_LOCATION_RIGHT, map.SPRITE_OFFSETS)
                }
