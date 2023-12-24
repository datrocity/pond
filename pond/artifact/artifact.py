from abc import ABC, abstractmethod
from typing import Type


class Artifact(ABC):
    """ Knows how to read and write one type of artifact.

    Concrete Artifact implementation should save the metadata with the data if possible,
    so that the artifact is self-contained even if, for instance, it is sent by email.
    """

    # --- Artifact class interface

    # todo: what is the class_id for?

    @classmethod
    def class_id(cls):
        """ String ID to be able to find this class from its name. """
        return cls.__name__

    @classmethod
    def subclass_from_id(cls, class_id: str) -> Type['Artifact']:
        """ Find a subclass from its class ID. """
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            if subclass.class_id() == class_id:
                break
        else:
            # todo this exception is not defined here
            raise InvalidArtifactClass(class_id)
        return subclass

    # --- Artifact public interface

    def __init__(self, data, metadata=None):
        """ Create an Artifact.

        Parameters
        ----------
        data: any
            The data of the artifact.
        metadata: dict
            User-defined metadata, saved with the artifact (optional).
            The metadata keys and values will be stored as strings.
        """
        self.data = data
        if metadata is None:
            metadata = {}
        self.metadata = metadata

    @classmethod
    def read(cls, path, metadata=None, **kwargs):
        """ Reads the artifact from a file, given the path.

        Parameters
        ----------
        path: str
            Filename from which the artifact is read.
        metadata: dict or None
            The metadata for the artifact. If defined, it takes the place of any metadata
            defined in the artifact itself.
            Typically, this external artifact metadata comes from an artifact manifest. If the
            artifact has been written as a `pond` `VersionedArtifact`, then the two sources of
            metadata are identical.
        kwargs: dict
            Additional parameters for the reader.

        Returns
        -------
        artifact: Artifact
            An instance of the artifact.
        """
        with open(path, 'rb') as f:
            artifact = cls.read_bytes(f, metadata, **kwargs)
        return artifact

    @classmethod
    def read_bytes(cls, file_, metadata=None, **kwargs):
        """ Reads the artifact from a binary file.

        Parameters
        ----------
        file_: file-like object
            A file-like object from which the artifact is read, opened in binary mode.
        metadata: dict or None
            The metadata for the artifact. If defined, it takes the place of any metadata
            defined in the artifact itself.
            Typically, this external artifact metadata comes from an artifact manifest. If the
            artifact has been written as a `pond` `VersionedArtifact`, then the two sources of
            metadata are identical.
        kwargs: dict
            Parameters for the reader.

        Returns
        -------
        artifact: Artifact
            An instance of the artifact.
        """
        artifact = cls._read_bytes(file_, **kwargs)
        if metadata is not None:
            artifact.metadata = metadata
        return artifact

    # todo why the kwargs
    def write(self, path, **kwargs):
        """ Writes the artifact to file.

        Parameters
        ----------
        path: str
            Path to which the artifact is written.
        kwargs: dict
            Parameters for the writer.

        """
        with open(path, 'wb') as f:
            self.write_bytes(f, **kwargs)

    # --- Abstract interface

    @staticmethod
    @abstractmethod
    def filename(basename):
        """ Complete a base filename with an extension.

        Parameters
        ----------
        basename: str
            The filename without extension.

        Returns
        -------
        filename: str
            The completed filename.

        """
        pass

    @classmethod
    @abstractmethod
    def _read_bytes(cls, file_, **kwargs):
        """ Reads the artifact from a binary file.

        This is a private method that loads the artifact from a binary file without dealing with
        the logic of the external metadata. It is called by `Artifact.read_bytes`.

        Parameters
        ----------
        file_: file-like object
            A file-like object from which the artifact is read, opened in binary mode.
        kwargs: dict
            Parameters for the reader.

        Returns
        -------
        artifact: Artifact
            An instance of the artifact.
        """
        pass

    @abstractmethod
    def write_bytes(self, file_, **kwargs):
        """ Writes the artifact to binary file.

        This method also need to take care of writing the artifact metadata in the file itself,
        whenever possible.
        If the artifact is being written as a `pond` `VersionedArtifact`, then the metadata is also
        stored in an external manifest.

        Parameters
        ----------
        file_: file-like object
            A file-like object to which the artifact is written, opened in binary mode.
        kwargs: dict
            Parameters for the writer.

        """
        pass

    def get_artifact_metadata(self):
        """
        This is not the user metadata!

        Returns
        -------

        """
        return None
