import pygame
import xml.etree
from PyTiledClasses import *


class Ghost(MapObject):
    def __init__(self, *args, **kwargs):
        super(Ghost, self).__init__(*args, **kwargs)


class Blinky(Ghost):
    def __init__(self, *args, **kwargs):
        super(Blinky, self).__init__(*args, **kwargs)


class Pinky(Ghost):
    def __init__(self, *args, **kwargs):
        super(Pinky, self).__init__(*args, **kwargs)


class Inky(Ghost):
    def __init__(self, *args, **kwargs):
        super(Inky, self).__init__(*args, **kwargs)


class Clyde(Ghost):
    def __init__(self, *args, **kwargs):
        super(Clyde, self).__init__(*args, **kwargs)


# class Layer:
#    def __init__(self, objects=[[]], hidden=False):
#        self.objects = objects
#        self.hidden = hidden
#
#    def draw(self, surface):
#        pass


# class Teleport(MapObject):
#     def touch(self, insta):
#         insta.x = self.port_x
#         insta.y = self.port_y


class Game:
    def __init__(self, mapname):
        self.points = 0
        self.map_ = Map(mapname)
        self.surface = pygame.Surface((self.map_.tile_width*self.map_.map_width,
                                       self.map_.tile_height*self.map_.map_height))
        self.game_over = False

    def add_point(self, value):
        self.points += value

    def draw(self, surface, dt):
        self.surface.fill((255,255,255))
        myfont = pygame.font.SysFont("monospace", 15)

        self.map_.draw(self.surface, dt)

        # render text
        label = myfont.render(str(self.points), 1, (255, 0, 0))
        self.surface.blit(label, (0, 0))

        if self.game_over:
            label = myfont.render("Game over", 1, (255, 0, 0))
            self.surface.blit(label, (100, 100))

        s = pygame.transform.scale(self.surface, surface.get_size())
        surface.blit(s, (0, 0))

    def update(self, dt):
        # self.map_.player.update(dt)
        if not self.game_over:
            dirs = {"right": (1, 0), "up": (0, -1), "left": (-1, 0), "down": (0, 1)}
            self.map_.player.prev_time += dt
            if self.map_.player.prev_time >= self.map_.player.speed:
                next_direction_free = True
                for layer in self.map_.layers:
                    next_direction_x = self.map_.player.x + dirs[self.map_.player.next_direction][0]
                    next_direction_y = self.map_.player.y + dirs[self.map_.player.next_direction][1]
                    next_direction_tile = layer[next_direction_y][next_direction_x]
                    if hasattr(next_direction_tile, "wall") and next_direction_tile.wall:
                        next_direction_free = False
                        break
                if next_direction_free:
                    self.map_.player.direction = self.map_.player.next_direction

                next_tile_free = True
                for layer in self.map_.layers:
                    next_tile_x = self.map_.player.x + dirs[self.map_.player.direction][0]
                    next_tile_y = self.map_.player.y + dirs[self.map_.player.direction][1]
                    next_tile = layer[next_tile_y][next_tile_x]
                    if hasattr(next_tile, "wall") and next_tile.wall:
                        next_tile_free = False
                        break

                if next_tile_free:
                    self.map_.player.x += dirs[self.map_.player.direction][0]
                    self.map_.player.y += dirs[self.map_.player.direction][1]
                    # self.map_.player.prev_time %= self.map_.player.speed
                    self.map_.player.prev_time = 0

                for f in self.map_.foods:
                    if f.x == self.map_.player.x and f.y == self.map_.player.y:
                        self.points += f.points
                        self.map_.foods.remove(f)

            if not self.map_.foods:
                self.game_over = True


class Pacman(MapObject):
    def __init__(self, direction="left", *args, **akws):
        super(Pacman, self).__init__(*args, **akws)
        self.direction = direction
        self.next_direction = direction

        self.prev_time = 0
        self.speed = 0.1
        self.image = load_tile("function", 0)
        self.image.scale(self.speed)

    def change_direction(self, value):
        self.next_direction = value

    def draw(self, surface, tile_width, tile_height, dt, offset=(0, 0)):
        dirs = {"right":0,"up":90,"left":180,"down":270}
        super(Pacman, self).draw(surface, tile_width, tile_height, dt, offset, rotate=dirs[self.direction])


class Food(MapObject):
    def __init__(self, points=1000, *args, **akws):
        super(Food, self).__init__(*args, **akws)
        self.points = points

    def active(self, game):
        game.add_point(self.points)
        game.remove_food(self)


def load_tile(name, id_=0):
    tree = xml.etree.ElementTree.parse("maps/" + name + ".tsx")
    image_path = tree._root[1].attrib["source"]
    image_path = image_path.replace("\\", "/")
    start = image_path.rfind("/")
    image_path = image_path[start:]
    image = pygame.image.load("data/images" + image_path)
    spacing_ = int(tree._root.attrib.get("spacing", 0))
    margin = int(tree._root.attrib.get("margin", 0))
    tilewidth = int(tree._root.attrib["tilewidth"])
    tileheight = int(tree._root.attrib["tileheight"])
    columns = int(tree._root.attrib["columns"])
    for element in tree._root:
        if element.tag == "tile" and int(element.attrib["id"]) == id_:
            animation = False
            for element2 in element:
                if element2.tag == "animation":
                    animation_element = element2
                    animation = True
            if animation:
                frames = []
                for f in animation_element:
                    frames.append(pygame.Surface.subsurface(image,
                                                            (int(f.attrib["tileid"]) % columns) *
                                                            (tilewidth + spacing_) + spacing_,
                                                            (int(f.attrib["tileid"]) // columns) *
                                                            (tileheight + margin) + margin,
                                                            tilewidth, tileheight))
                    frames.append(float(f.attrib["duration"])/1000.0)
                    # frames.append(None)
                # if not loop:
                #    frames = frames[:-2]
                return Animation(frames)
    im = pygame.Surface.subsurface(image, ((id_ % columns) * (tilewidth + spacing_) + spacing_,
                                           (id_ // columns) * (tileheight + margin) + margin, tilewidth, tileheight))
    return im
