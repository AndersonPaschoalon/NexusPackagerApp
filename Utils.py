import os
import os.path
from termcolor import colored
import shutil


class Utils:

    @staticmethod
    def echo_error(message: str):
        print(colored(message, 'red'))

    @staticmethod
    def echo_warn(message: str):
        print(colored(message, 'yellow'))

    @staticmethod
    def echo_info(message: str):
        print(message)

    @staticmethod
    def scandir(dir, ext):  # dir: str, ext: list
        # https://stackoverflow.com/a/59803793/2441026
        subfolders, files = [], []
        for f in os.scandir(dir):
            if f.is_dir():
                subfolders.append(f.path)
            if f.is_file():
                if os.path.splitext(f.name)[1].lower() in ext:
                    files.append(f.path)
        for dir in list(subfolders):
            sf, f = Utils.scandir(dir, ext)
            subfolders.extend(sf)
            files.extend(f)
        return subfolders, files

    @staticmethod
    def copytree(src: str, dst: str):
        dstfolder = os.path.dirname(dst)
        if not os.path.exists(dstfolder) and dstfolder != "":
            os.makedirs(dstfolder)
        print(src + " -> " + dst)
        shutil.copy(src, dst)

