from abc import ABC, abstractmethod
from typing import Type

import joblib

from pond.metadata.dict import DictMetadataSource


class Artifact(ABC):
    """ Knows how to read and write one type of artifact.

    Concrete Artifact implementation should save the metadata with the data if possible,
    so that the artifact is self-contained even if, for instance, it is sent by email.
    """

    # --- Artifact class interface

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

    def __init__(self, data, metadata=None, data_hash=None):
        """ Create an Artifact.

        Parameters
        ----------
        data: any
            The data of the artifact.
        metadata: dict
            User-defined metadata, saved with the artifact (optional).
            The metadata keys and values will be stored as strings.
        data_hash: str
            The data hash of the data, if known (for example, when the artifact
            is read from a Version). If None, the hash is re-computed.
        """

        self.data = data

        if data_hash is None:
            data_hash = self._data_hash()
        self.data_hash = data_hash

        if metadata is None:
            metadata = {}
        self.metadata = metadata

    # --- Artifact abstract interface

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
        data_hash: str
            The data hash of the data, if known (for example, when the artifact
            is read from a Version). If None, the hash is re-computed.
        kwargs: dict
            Parameters for the reader.

        Returns
        -------
        data: any
            The data of the artifact.
        metadata: dict
            User-defined metadata, saved with the artifact (optional).
            The metadata keys and values will be stored as strings.
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

    # --- Artifact public interface

    @classmethod
    def read_bytes(cls, file_, metadata=None, data_hash=None, **kwargs):
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
        data_hash: str
            The data hash of the data, if known (for example, when the artifact
            is read from a Version). If None, the hash is re-computed.
        kwargs: dict
            Parameters for the reader.

        Returns
        -------
        artifact: Artifact
            An instance of the artifact.
        """
        data, read_metadata = cls._read_bytes(file_, **kwargs)
        if metadata is None:
            metadata = read_metadata

        return cls(data, metadata=metadata, data_hash=data_hash)

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

    def get_artifact_metadata(self):
        """
        This is not the user metadata!

        Returns
        -------

        """
        artifact_metadata = {
            'data_hash': self.data_hash,
        }
        artifact_metadata_source = DictMetadataSource(name='artifact', metadata=artifact_metadata)
        return artifact_metadata_source

    # --- Artifact private interface

    def _data_hash(self):
        return joblib.hash(self.data)
