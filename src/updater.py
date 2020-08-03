from git import Repo
import os
from pathlib import Path


class Updater:
    def __init__(self):
        dirpath = os.path.dirname(__file__)
        self.git_path = os.path.join(dirpath, "..")

    # TODO: Build more complex Structure to test for new release first and only update to release
    # TODO: Also prompt user if he wants to upgrade to release version x.x.x from x.x.x
    def update(self):
        repo = Repo(self.git_path)
        repo.remotes.origin.pull()
