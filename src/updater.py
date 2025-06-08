from git import Repo

from src.filepath import ROOT_PATH


class Updater:
    def __init__(self) -> None:
        """Class to handle the update process of the application."""
        self.git_path = ROOT_PATH

    # TODO: Build more complex Structure to test for new release first and only update to release
    # TODO: Also prompt user if he wants to upgrade to release version x.x.x from x.x.x
    def update(self) -> None:
        repo = Repo(self.git_path)
        repo.remotes.origin.pull()


UPDATER = Updater()
