import time
import sys
import pygame
import PyTiledClasses
import os
import importlib.util
import tarfile
import tempfile


def main():
    if len(sys.argv) < 2:
        raise Exception("Pass project folder!")

    project_working_dir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(project_working_dir) and \
            os.path.isfile(project_working_dir + ".pyt") and \
            tarfile.is_tarfile(project_working_dir + ".pyt"):
        temp_project_working_dir = tempfile.mkdtemp()
        tar = tarfile.open(project_working_dir + ".pyt")
        tar.extractall(path=temp_project_working_dir)
        tar.close()
        project_working_dir = temp_project_working_dir
    elif not os.path.isdir(project_working_dir):
        raise Exception("Project don't exists")

    spec = importlib.util.spec_from_file_location("game", os.path.join(project_working_dir, "init.py"))
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)
    PyTiledClasses.PROJECT_PATH = project_working_dir

    pygame.init()

    screen_width, screen_height = 640, 480
    screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    surface.fill((255, 255, 255))

    game = plugin.Game("main")

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
