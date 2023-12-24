import numpy as np

from pond.artifact import Artifact
from pond.artifact.artifact_registry import global_artifact_registry


class NumpyArrayArtifact(Artifact):
    """ Artifact for numpy arrays.

    The array is saved in .npz format. This format allows to store numpy arrays without installing an additional
    dependency, and to include the metadata as an additional array in the file itself.
    """

    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        """ Read a numpy array from a npy binary file. """
        content = np.load(file_, allow_pickle=True)
        data = content['data']
        metadata = content['metadata'][()]
        return cls(data, metadata=metadata)

    def write_bytes(self, file_):
        # The pond convention is that all stored metadata is a string
        metadata = {k: str(v) for k, v in self.metadata.items()}
        metadata_array = np.array(metadata)
        np.savez_compressed(file_, data=self.data, metadata=metadata_array)

    @staticmethod
    def filename(basename):
        return basename + '.npz'


global_artifact_registry.register(artifact_class=NumpyArrayArtifact, data_class=np.array, format='npz')
