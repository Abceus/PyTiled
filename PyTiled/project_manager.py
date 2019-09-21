import os
import tempfile
import tarfile
import importlib
import shutil


class ProjectManager:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if ProjectManager.__instance is None:
            ProjectManager()
        return ProjectManager.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ProjectManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ProjectManager.__instance = self
            self.path = ""
            self.module = None
            self.archived = False
            self.game = None

    def load_game(self, path):
        archived = False
        path = os.path.abspath(path)
        if self.archived and self.path:
            shutil.rmtree(self.path)
        self.game = None
        self.archived = False
        if not os.path.isdir(path):
            if os.path.splitext(path)[1] != ".pyt":
                path = path + ".pyt"
            if os.path.isfile(path) and tarfile.is_tarfile(path):
                temp_path = tempfile.mkdtemp()
                tar = tarfile.open(path)
                tar.extractall(path=temp_path)
                tar.close()
                path = temp_path
                archived = True
            else:
                raise Exception("Project don't exists")

        spec = importlib.util.spec_from_file_location("game", os.path.join(path, "init.py"))
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)
        self.path = path
        self.module = plugin
        self.archived = archived

    def get_game(self):
        if self.module is None:
            return None
        if self.game is not None:
            return self.game
        self.game = self.module.Game("main")
        return self.game

    def event(self, event):
        if self.get_game() is not None:
            self.get_game().event(event)

    def update(self, dt):
        if self.get_game() is not None:
            self.get_game().update(dt)

    def draw(self, surface, dt):
        if self.get_game() is not None:
            self.get_game().draw(surface, dt)

    def __del__(self):
        if self.archived and self.path:
            shutil.rmtree(self.path)

def get_project_manager():
    return ProjectManager.get_instance()
