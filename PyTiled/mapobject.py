import pygame

from PyTiled.animation import Animation


class MapObject:
    def __init__(self, x=0, y=0, image=None, hidden=False, properties=None):
        if properties:
            for property_ in properties:
                setattr(self, property_.name, property_.value)
        self.x = x
        self.y = y
        self.image = image
        self.hidden = hidden

    def draw(self, surface, tile_width, tile_height, dt, offset=(0, 0), rotate=0):
        if type(self.image) == Animation:
            self.image.update_image(dt)
            self.image.image = pygame.transform.rotate(self.image.image, rotate)
            surface.blit(self.image.image, (self.x*tile_width+offset[0]-tile_width/2,
                                            self.y*tile_height+offset[1]-tile_width/2))
        else:
            if self.image:
                surface.blit(self.image, (self.x*tile_width+offset[0]-tile_width/2,
                                          self.y*tile_height+offset[1]-tile_width/2))
