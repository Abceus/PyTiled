import tarfile
import sys
import os


def main():
    if len(sys.argv) < 3:
        raise Exception("Too few arguments.")
    dist_path = os.path.join(os.getcwd(), "dist")
    if not os.path.exists(dist_path):
        os.makedirs(dist_path)
    with tarfile.open(os.path.join(dist_path, sys.argv[2] + ".pyt"), "w") as tar:
        for filename in os.listdir(os.path.abspath(sys.argv[1])):
            full_path = os.path.join(os.path.abspath(sys.argv[1]), filename)
            tar.add(full_path, arcname=filename)


if __name__ == '__main__':
    main()
