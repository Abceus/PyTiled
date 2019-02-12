import pygame
import sys
import tmx
import copy
import inspect
import os


class Project:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Project.__instance is None:
            Project()
        return Project.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Project.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Project.__instance = self
            self.path = ""
            self.module = None

# PROJECT_PATH = ""
# PROJECT_MODULE = None


class Animation:
    def __init__(self, frames=None):
        self.frames = frames if frames else []
        self.image = frames[-2]
        self.dt = 0
        # self.repeat = (len(times) == len(images))

    def scale(self, time_):
        s = sum([self.frames[i] for i in range(len(self.frames)) if i % 2 == 1])
        for fi in range(len(self.frames)):
            if fi % 2 == 1:
                self.frames[fi] = self.frames[fi]/s*time_

    def update_image(self, dt):
        self.dt += dt
        self.dt %= sum([self.frames[i] for i in range(len(self.frames)) if i % 2 == 1])
        tmp = 0
        i = 1
        while self.dt > tmp and i < len(self.frames):
            tmp += self.frames[i]
            i += 2
        self.image = self.frames[i-3]


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
            surface.blit(self.image, (self.x*tile_width+offset[0]-tile_width/2,
                                      self.y*tile_height+offset[1]-tile_width/2))

class Map:
    def __init__(self, filename):

        # self.foods = []
        # self.ghosts = []
        self.layers = []
        self.groups = {}

        map_ = tmx.TileMap.load(os.path.join(Project.get_instance().path, "maps", filename + ".tmx"))
        # map_ = tmx.TileMap.load(PROJECT_PATH + "maps/" + filename + ".tmx")

        # self.name = filename
        self.map_width = map_.width
        self.map_height = map_.height
        self.tile_width = map_.tilewidth
        self.tile_height = map_.tileheight

        self.tiles = []
        # First tile - empty tile
        empty_object = MapObject()
        # empty_object.hide = True
        self.tiles.append(empty_object)

        for ts in map_.tilesets:
            image_path = ts.image.source.replace("\\", "/")
            start = image_path.rfind("/")
            image_path = image_path[start:]
            # TODO: os.join
            impath = os.path.join(Project.get_instance().path, "data/images")
            image = pygame.image.load(os.path.join(Project.get_instance().path, "data/images", image_path[1:]))
            spacing_ = ts.spacing
            margin = ts.margin
            tilewidth = ts.tilewidth
            tileheight = ts.tileheight
            columns = ts.columns
            for i in range(ts.tilecount):
                im = None
                if i >= len(ts.tiles) or ts.tiles[i].animation is None:
                    im = pygame.Surface.subsurface(image,
                                                   ((i % columns) * (tilewidth + spacing_) + spacing_,
                                                    (i // columns) * (tileheight + margin) + margin,
                                                    tilewidth, tileheight))
                else:
                    pass
                #    frames = []
                #    for f in ts.tiles[i].animation:
                #        frames.append(renpy.display.transform.Transform(child=image, \
                #                        crop = ((f.tileid % columns) * (tilewidth + spacing_) + spacing_,
                #                        (f.tileid // columns) * (tileheight + margin) + margin, \
                #                        tilewidth, tileheight)))
                #        frames.append(f.duration/1000.0)
                #        frames.append(None)
                #    im = renpy.display.anim.TransitionAnimation(*frames)

                properties = []
                class_ = getattr(sys.modules[__name__], "MapObject")
                for tile in ts.tiles:
                    if tile.id == i:
                        properties = tile.properties
                for p in properties:
                    if p.name == "class_":
                        if hasattr(sys.modules[__name__], p.value):
                            class_ = getattr(sys.modules[__name__], p.value)
                        elif Project.get_instance().module and hasattr(Project.get_instance().module, p.value):
                            class_ = getattr(Project.get_instance().module, p.value)
                class_args = inspect.getfullargspec(class_).args
                cl_args = {}
                for p in properties:
                    if p.name in class_args:
                        cl_args[p.name] = p.value

                t = class_(image=im, properties=properties, **cl_args)
                self.tiles.append(t)

        for layer in map_.layers:
            type_ = None

            for p in layer.properties:
                if p.name == "type":
                    type_ = p.value

            if type_ == "dynamic":
                for i in range(len(layer.tiles)):
                    y = i // self.map_width
                    x = i % self.map_width
                    if layer.tiles[i].gid != 0:
                        new_object = copy.copy(self.tiles[layer.tiles[i].gid])
                        new_object.x = x
                        new_object.y = y
                        if hasattr(new_object, "group") and new_object.group:
                            group = self.groups.get(new_object.group, None)
                            if group:
                                if isinstance(group, list):
                                    group.append(new_object)
                                else:
                                    old_group = group
                                    self.groups[new_object.group] = []
                                    self.groups[new_object.group].append(old_group)
                                    self.groups[new_object.group].append(new_object)
                            else:
                                self.groups[new_object.group] = new_object
            else:
                self.layers.append([])
                for i in range(len(layer.tiles)):
                    if i % self.map_width == 0:
                        self.layers[-1].append([])
                    self.layers[-1][-1].append(self.tiles[layer.tiles[i].gid])

    def draw(self, surface, dt):
        for layer in self.layers:
            for rowi in range(len(layer)):
                row = layer[rowi]
                for oi in range(len(row)):
                    o = row[oi]
                    o.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt,
                           offset=(oi * self.tile_height, rowi * self.tile_width))

        for group_key, group_value in self.groups.items():
            if isinstance(group_value, list):
                for item in group_value:
                    item.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt)
            else:
                group_value.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt)

        # for g in self.ghosts:
        #     g.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt)
        #
        # for f in self.foods:
        #     f.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt)
        #
        # self.player.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt,
        #                     offset=(-self.player.image.frames[0].get_size()[0] / 4,
        #                             -self.player.image.frames[0].get_size()[1] / 4))
        # self.player.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt)

    def get_group(self, key):
        return self.groups.get(key, None)
