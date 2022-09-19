import os


class Cd:
    """Context manager for changing the current working directory"""

    def __init__(self, new_path: str):
        self.newPathStr = new_path.strip()
        self.newPath = os.path.expanduser(new_path)

    def __enter__(self):
        if self.newPathStr != "" and self.newPathStr != ".":
            self.savedPath = os.getcwd()
            os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        if self.newPathStr != "" and self.newPathStr != ".":
            os.chdir(self.savedPath)

    @staticmethod
    def pwd():
        """
        Returns the current working directory.
        :return:
        """
        return os.getcwd()
