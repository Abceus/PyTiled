import pygame
import xml.etree
import os
import importlib.util
import tarfile
import tempfile


from PyTiled import project
import PyTiled


# TODO: load tmx
def load_tmx(path):
    import tmx
    return tmx.TileMap.load(path)


def load_tile(name, id_=0):
    # TODO: fix tileset path
    tree = xml.etree.ElementTree.parse(os.path.join(project.Project.get_instance().path, "maps", name + ".tsx"))
    # check if source exists
    source = None
    for node in tree._root:
        try:
            source = node.attrib["source"]
            break
        except KeyError:
            pass
    if source is None:
        return None

    image_path = source
    image_path = image_path.replace("\\", "/")
    start = image_path.rfind("/")
    image_path = image_path[start:]
    image = pygame.image.load(os.path.join(project.Project.get_instance().path, "data", "images", image_path[1:]))
    # image = pygame.image.load(os.path.join(project.Project.get_instance().path, image_path))
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
                return PyTiled.animation.Animation(frames)
    im = pygame.Surface.subsurface(image, ((id_ % columns) * (tilewidth + spacing_) + spacing_,
                                           (id_ // columns) * (tileheight + margin) + margin, tilewidth, tileheight))
    return im


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
