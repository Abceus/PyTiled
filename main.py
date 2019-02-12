import pygame
import sys
import tmx
import copy
import inspect
import time
import xml.etree


class Animation:
    def __init__(self, frames=None):
        self.frames = frames if frames else []
        self.image = frames[-2]
        self.dt = 0
        # self.repeat = (len(times) == len(images))

    def scale(self, time_):
        s = sum([self.frames[i] for i in range(len(self.frames)) if i % 2 == 1])
        for fi in range(len(self.frames)):
            if fi%2 == 1:
                self.frames[fi] = self.frames[fi]/s*time_

    def update_image(self, dt):
        self.dt += dt
        self.dt %= sum([self.frames[i] for i in range(len(self.frames)) if i % 2 == 1])
        # print(sum([self.frames[i] for i in range(len(self.frames)) if i%2==1]))
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

    def draw(self, surface, tile_width, tile_height, dt, offset=(0,0), rotate=0):
        if type(self.image) == Animation:
            self.image.update_image(dt)
            self.image.image = pygame.transform.rotate(self.image.image, rotate)
            surface.blit(self.image.image, (self.x*tile_width+offset[0]-tile_width/2,
                                            self.y*tile_height+offset[1]-tile_width/2))
        else:
            surface.blit(self.image, (self.x*tile_width+offset[0]-tile_width/2,
                                      self.y*tile_height+offset[1]-tile_width/2))


class Ghost(MapObject):
    def __init__(self, *args, **akws):
        super(Ghost, self).__init__(*args, **akws)


class Blinky(Ghost):
    def __init__(self, *args, **akws):
        super(Blinky, self).__init__(*args, **akws)


class Pinky(Ghost):
    def __init__(self, *args, **akws):
        super(Pinky, self).__init__(*args, **akws)


class Inky(Ghost):
    def __init__(self, *args, **akws):
        super(Inky, self).__init__(*args, **akws)


class Clyde(Ghost):
    def __init__(self, *args, **akws):
        super(Clyde, self).__init__(*args, **akws)


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


class Map:
    def __init__(self, filename):

        self.foods = []
        self.ghosts = []
        self.layers = []

        map_ = tmx.TileMap.load("maps/" + filename + ".tmx")

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
            image = pygame.image.load("./data/images" + image_path)
            spacing_ = ts.spacing
            margin = ts.margin
            tilewidth = ts.tilewidth
            tileheight = ts.tileheight
            columns = ts.columns
            for i in range(ts.tilecount):
                im = None
                if i >= len(ts.tiles) or ts.tiles[i].animation is None:
                    im = pygame.Surface.subsurface(image, ((i % columns) * (tilewidth + spacing_) + spacing_,
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
                class_name = "MapObject"
                for tile in ts.tiles:
                    if tile.id == i:
                        properties = tile.properties
                for p in properties:
                    if p.name == "class_" and hasattr(sys.modules[__name__], p.value):
                        class_name = p.value
                class_ = getattr(sys.modules[__name__], class_name)
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
                        # print(type(new_object), isinstance(new_object, Food))
                        if isinstance(new_object, Food):
                            self.foods.append(new_object)
                        elif isinstance(new_object, Pacman):
                            self.player = new_object
                        elif isinstance(new_object, Ghost):
                            self.ghosts.append(new_object)
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
                           offset=(oi*self.tile_height, rowi*self.tile_width))

        for g in self.ghosts:
            g.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt)

        for f in self.foods:
            f.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt)

        self.player.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt,
                         offset=(-self.player.image.frames[0].get_size()[0]/4,
                                 -self.player.image.frames[0].get_size()[1]/4))
        # self.player.draw(surface, tile_width=self.tile_width, tile_height=self.tile_height, dt=dt)


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


def main():
    pygame.init()

    screen_width, screen_height = 640, 480
    screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    surface.fill((255, 255, 255))

    game = Game("main")

    time.clock()
    prev_time = 0

    # pygame.key.set_repeat(1, 40)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    game.map_.player.change_direction("left")
                elif event.key == pygame.K_RIGHT:
                    game.map_.player.change_direction("right")
                elif event.key == pygame.K_UP:
                    game.map_.player.change_direction("up")
                elif event.key == pygame.K_DOWN:
                    game.map_.player.change_direction("down")

        surface.fill((255, 255, 255))
        game.update(time.clock() - prev_time)
        game.draw(surface, time.clock() - prev_time)
        prev_time = time.clock()
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        pygame.display.update()


if __name__ == '__main__':
    main()
