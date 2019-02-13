import pygame
import xml.etree
import os
from PyTiled import *
import PyTiled


class Ghost(mapobject.MapObject):
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


# class Teleport(MapObject):
#     def touch(self, insta):
#         insta.x = self.port_x
#         insta.y = self.port_y


class Game:
    def __init__(self, mapname):
        self.points = 0
        self.map_ = map.Map(mapname)
        self.surface = pygame.Surface((self.map_.tile_width*self.map_.map_width,
                                       self.map_.tile_height*self.map_.map_height))
        self.game_over = False

    def add_point(self, value):
        self.points += value

    def draw(self, surface, dt):
        self.surface.fill((255, 255, 255))
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
        player = self.map_.get_group("player")
        foods = self.map_.get_group("foods")
        if not self.game_over:
            dirs = {"right": (1, 0), "up": (0, -1), "left": (-1, 0), "down": (0, 1)}
            player.prev_time += dt
            if player.prev_time >= player.speed:
                next_direction_free = True
                for layer in self.map_.layers:
                    next_direction_x = player.x + dirs[player.next_direction][0]
                    next_direction_y = player.y + dirs[player.next_direction][1]
                    next_direction_tile = layer[next_direction_y][next_direction_x]
                    if hasattr(next_direction_tile, "wall") and next_direction_tile.wall:
                        next_direction_free = False
                        break
                if next_direction_free:
                    player.direction = player.next_direction

                next_tile_free = True
                for layer in self.map_.layers:
                    next_tile_x = player.x + dirs[player.direction][0]
                    next_tile_y = player.y + dirs[player.direction][1]
                    next_tile = layer[next_tile_y][next_tile_x]
                    if hasattr(next_tile, "wall") and next_tile.wall:
                        next_tile_free = False
                        break

                if next_tile_free:
                    player.x += dirs[player.direction][0]
                    player.y += dirs[player.direction][1]
                    # self.map_.player.prev_time %= self.map_.player.speed
                    player.prev_time = 0

                for f in foods:
                    if f.x == player.x and f.y == player.y:
                        self.points += f.points
                        self.map_.destroy_object(f)
                        # foods.remove(f)

            if not foods:
                self.game_over = True

    def event(self, event):
        if event.type == pygame.KEYUP:
            player = self.map_.get_group("player")
            if event.key == pygame.K_LEFT:
                player.change_direction("left")
            elif event.key == pygame.K_RIGHT:
                player.change_direction("right")
            elif event.key == pygame.K_UP:
                player.change_direction("up")
            elif event.key == pygame.K_DOWN:
                player.change_direction("down")


class Pacman(mapobject.MapObject):
    def __init__(self, direction="left", *args, **akws):
        super(Pacman, self).__init__(*args, **akws)
        self.direction = direction
        self.next_direction = direction

        self.prev_time = 0
        self.speed = 0.1
        self.image = utils.load_tile("function", 0)
        # TODO: ???? if not animation - crash
        self.image.scale(self.speed)

    def change_direction(self, value):
        self.next_direction = value

    def draw(self, surface, tile_width, tile_height, dt, offset=(0, 0)):
        dirs = {"right":0,"up":90,"left":180,"down":270}
        super(Pacman, self).draw(surface, tile_width, tile_height, dt, offset, rotate=dirs[self.direction])


class Food(mapobject.MapObject):
    def __init__(self, points=1000, *args, **akws):
        super(Food, self).__init__(*args, **akws)
        self.points = points

    def active(self, game):
        game.add_point(self.points)
        game.remove_food(self)
