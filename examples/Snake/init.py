import pygame
from PyTiled import *


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

        label = myfont.render(str(self.points), 1, (255, 0, 0))
        self.surface.blit(label, (0, 0))

        if self.game_over:
            label = myfont.render("Game over", 1, (255, 0, 0))
            self.surface.blit(label, (100, 100))

        s = pygame.transform.scale(self.surface, surface.get_size())
        surface.blit(s, (0, 0))

    def update(self, dt):
        head = self.map_.get_group("head")
        if not self.game_over:
            dirs = {"right": (1, 0), "up": (0, -1), "left": (-1, 0), "down": (0, 1)}
            head.prev_time += dt
            if head.prev_time >= head.speed:
                next_tile_free = True
                # for layer in self.map_.layers:
                #     next_tile_x = head.x + dirs[head.direction][0]
                #     next_tile_y = head.y + dirs[head.direction][1]
                #     next_tile = layer[next_tile_y][next_tile_x]
                #     if hasattr(next_tile, "wall") and next_tile.wall:
                #         next_tile_free = False
                #         break

                if next_tile_free:
                    head.x += dirs[head.direction][0]
                    head.y += dirs[head.direction][1]
                    head.prev_time = 0

                # for f in foods:
                #     if f.x == player.x and f.y == player.y:
                #         self.points += f.points
                #         self.map_.destroy_object(f)

            # if not foods:
            #     self.game_over = True

    def event(self, event):
        if event.type == pygame.KEYUP:
            player = self.map_.get_group("head")
            if event.key == pygame.K_LEFT:
                player.change_direction("left")
            elif event.key == pygame.K_RIGHT:
                player.change_direction("right")
            elif event.key == pygame.K_UP:
                player.change_direction("up")
            elif event.key == pygame.K_DOWN:
                player.change_direction("down")


class SnakeHead(mapobject.MapObject):
    def __init__(self, direction="left", *args, **akws):
        super(SnakeHead, self).__init__(*args, **akws)
        self.direction = direction

        self.prev_time = 0
        self.speed = 0.1
        # ???
        self.image = utils.load_tile("main_tileset", 49)

    def change_direction(self, value):
        self.next_direction = value

    def draw(self, surface, tile_width, tile_height, dt, offset=(0, 0)):
        dirs = {"right": 0, "up": 90, "left": 180, "down": 270}
        super(SnakeHead, self).draw(surface, tile_width, tile_height, dt, offset, rotate=dirs[self.direction])
