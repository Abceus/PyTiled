import time
import sys
import pygame
from PyTiled import *
import os
import importlib.util
import tarfile
import tempfile


def load_game(path):
    if not os.path.isdir(path) and \
            os.path.isfile(path + ".pyt") and \
            tarfile.is_tarfile(path + ".pyt"):
        temp_path = tempfile.mkdtemp()
        tar = tarfile.open(path + ".pyt")
        tar.extractall(path=temp_path)
        tar.close()
        path = temp_path
    elif not os.path.isdir(path):
        raise Exception("Project don't exists")

    spec = importlib.util.spec_from_file_location("game", os.path.join(path, "init.py"))
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)
    project.Project.get_instance().path = path
    project.Project.get_instance().module = plugin
    spec = importlib.util.spec_from_file_location("game", os.path.join(path, "init.py"))
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)
    project.Project.get_instance().path = path
    project.Project.get_instance().module = plugin


def main():
    if len(sys.argv) < 2:
        raise Exception("Pass project folder!")

    project_working_dir = os.path.abspath(sys.argv[1])
    load_game(project_working_dir)

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
            elif event.type == pygame.KEYUP:
                player = game.map_.get_group("player")
                if event.key == pygame.K_LEFT:
                    player.change_direction("left")
                elif event.key == pygame.K_RIGHT:
                    player.change_direction("right")
                elif event.key == pygame.K_UP:
                    player.change_direction("up")
                elif event.key == pygame.K_DOWN:
                    player.change_direction("down")
                elif event.key == pygame.K_r:
                    load_game(project_working_dir)
                    game = project.Project.get_instance().module.Game("main")

        surface.fill((255, 255, 255))
        game.update(time.clock() - prev_time)
        game.draw(surface, time.clock() - prev_time)
        prev_time = time.clock()
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        pygame.display.update()


if __name__ == '__main__':
    main()
