import time
import sys
import pygame
from PyTiled import *
from PyTiled.project_manager import get_project_manager
import os
import shutil


def main():
    if len(sys.argv) < 2:
        raise Exception("Pass project folder!")

    project_working_dir = os.path.abspath(sys.argv[1])
    get_project_manager().load_game(project_working_dir)

    pygame.init()

    screen_width, screen_height = 640, 480
    screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    surface.fill((255, 255, 255))

    game = get_project_manager().get_game()

    time.clock()
    prev_time = 0

    # pygame.key.set_repeat(1, 40)

    while True:

        for event in pygame.event.get():
            game.event(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        surface.fill((255, 255, 255))
        game.update(time.clock() - prev_time)
        game.draw(surface, time.clock() - prev_time)
        prev_time = time.clock()
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        pygame.display.update()


if __name__ == '__main__':
    main()
