import os
from shutil import rmtree
from typing import Any, IO

from pond.storage.datastore import Datastore


class FileDatastore(Datastore):
    """Datastore based on a regular file system.

    Parameters
    ----------
    id: str
        Unique identifier for the datastore. This is used in the URI for each versioned
        artifact to uniquely identify the artifact.
    base_path: str
        Filesystem path at which the data store is based.

    Raises
    ------
    FileNotFoundError
        If `base_path` does not exist.
    NotADirectoryError
        If `base_path` exists but is not a directory.
    """

    def __init__(self, id: str, base_path: str):
        if not os.path.exists(base_path):
            raise FileNotFoundError(f'Base path {base_path} does not exist')
        if not os.path.isdir(base_path):
            raise NotADirectoryError(f'Base path {base_path} exists but is not a directory')

        super().__init__(id)
        self.base_path = base_path

    # -- Datastore interface

    def open(self, path: str, mode: str) -> IO[Any]:
        path = os.path.join(self.base_path, path)
        return open(path, mode)

    def read(self, path: str) -> bytes:
        with self.open(path, 'rb') as f:
            data = f.read()
        return data

    def write(self, path: str, data: bytes) -> None:
        self.makedirs(os.path.dirname(path))
        with self.open(path, 'wb') as f:
            f.write(data)

    def exists(self, path: str) -> bool:
        """ Returns True if the file exists.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.

        Returns
        -------
        bool
            True if the file exists, false otherwise
        """
        complete_path = os.path.join(self.base_path, path)
        return os.path.exists(complete_path)

    def delete(self, path: str, recursive: bool = False) -> None:
        complete_path = os.path.join(self.base_path, path)
        if os.path.exists(complete_path):
            if recursive:
                rmtree(complete_path)
            else:
                os.remove(complete_path)

    def makedirs(self, path: str) -> None:
        """ Creates the specified directory if needed.

        If the directories already exist, the method does not do anything.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        """
        complete_path = os.path.join(self.base_path, path)
        os.makedirs(complete_path, exist_ok=True)
