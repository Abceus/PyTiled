import time
import sys
import pygame
from PyTiled import *
import os


def main():
    if len(sys.argv) < 2:
        raise Exception("Pass project folder!")

    project_working_dir = os.path.abspath(sys.argv[1])
    utils.load_game(project_working_dir)

    pygame.init()

    screen_width, screen_height = 640, 480
    screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    surface.fill((255, 255, 255))

    game = project.Project.get_instance().module.Game("main")

    time.clock()
    prev_time = 0

    # pygame.key.set_repeat(1, 40)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.event(event)

        surface.fill((255, 255, 255))
        game.update(time.clock() - prev_time)
        game.draw(surface, time.clock() - prev_time)
        prev_time = time.clock()
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        pygame.display.update()


if __name__ == '__main__':
    main()
