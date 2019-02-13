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
