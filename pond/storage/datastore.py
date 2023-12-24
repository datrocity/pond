from abc import ABC, abstractmethod
import json
from typing import Any, IO

from pond.conventions import TXT_ENCODING
from pond.yaml import yaml_dump, yaml_load


class Datastore(ABC):
    """ Versioned storage for the artifacts.

    Parameters
    ----------
    id: str
        Unique identifier for the datastore. This is used in the URI for each versioned
        artifact to uniquely identify the artifact.
    """

    # -- Datastore class interface

    def __init__(self, id: str):
        self.id = id

    # -- Abstract interface

    @abstractmethod
    def open(self, path: str, mode: str) -> IO[Any]:
        """ Open a file-like object

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        mode: str
            Specifies the mode in which the file is opened.

        Returns
        -------
        IO[Any]
            An open file-like object.

        """
        pass

    @abstractmethod
    def read(self, path: str) -> bytes:
        """ Read a sequence of bytes from the data store.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.

        Returns
        -------
        bytes
            The sequence of bytes read from `path`.

        Raises
        ------
        FileNotFoundError
            If the requested path does not exist.
        """
        pass

    @abstractmethod
    def write(self, path: str, data: bytes) -> None:
        """ Write a sequence of bytes to the data store.

        `path` contains the path relative to the root of the data store, including the name
        of the file to be created. If a file already exists at `path`, it is overwritten.

        Intermediate directories that do not exist will be created.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        data: bytes
            Sequence of bytes to write at `path`.
        """
        pass

    @abstractmethod
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
        ...

    @abstractmethod
    def delete(self, path: str, recursive: bool = False) -> None:
        """Deletes a file or directory
        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        recursive: bool, optional, default is False
            Whether to recursively delete the location
        """
        ...

    @abstractmethod
    def makedirs(self, path: str) -> None:
        """ Creates the specified directory if needed.

        If the directories already exist, the method does not do anything.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        """
        ...

    # -- Read/write utility methods

    def read_string(self, path: str) -> str:
        """ Read a string from a file.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.

        Returns
        -------
        str
            The read string

        Raises
        ------
        FileNotFound
            If the file cannot be found
        """
        return self.read(path).decode(TXT_ENCODING)

    def write_string(self, path: str, content: str) -> None:
        """ Write a string to a file.

        Intermediate directories that do not exist will be created.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.

        content: str
            Content to write
        """
        self.write(path, content.encode(TXT_ENCODING))

    def read_yaml(self, path: str) -> Any:
        """ Read and parse a YAML file.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.

        Returns
        -------
        Any
            The parsed object

        Raises
        ------
        FileNotFound
            If the file cannot be found
        """
        return yaml_load(self.read_string(path))

    def write_yaml(self, path: str, content: Any) -> None:
        """ Serializes to YAML and write an object to a file.

        Intermediate directories that do not exist will be created.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        content: Any
            Content to write
        """
        return self.write_string(path, yaml_dump(content))

    def read_json(self, path: str) -> Any:
        """ Read and parse a JSON file.

        Parameters
        ----------
        path: str
            Path relative to the root of the data store.

        Returns
        -------
        Any
            The parsed object

        Raises
        ------
        FileNotFound
            If the file cannot be found
        """
        return json.loads(self.read_string(path))

    def write_json(self, path: str, content: Any) -> None:
        """Serializes to JSON and write an object to a file
        Parameters
        ----------
        path: str
            Path relative to the root of the data store.
        content: Any
            Content to write
        """
        return self.write_string(path, json.dumps(content, separators=(',', ':')))
