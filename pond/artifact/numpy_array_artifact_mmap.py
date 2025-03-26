import numpy as np

from pond.artifact import Artifact
from pond.artifact.artifact_registry import global_artifact_registry


class NumpyArrayArtifactMmap(Artifact):
    """ Artifact for numpy arrays.

    The array is saved in .npz format. This format allows to store numpy arrays without installing an additional
    dependency, and to include the metadata as an additional array in the file itself.
    """

    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        """ Read a numpy array from a npy binary file. """

        data = np.load(file_.name, allow_pickle=True, mmap_mode="r")

        # how to load the metadata here???
        #data = content['data']
        #metadata = content['metadata'][()]
        metadata = None
        return data, metadata

    def write_bytes(self, file_):
        # The pond convention is that all stored metadata is a string
        metadata = {k: str(v) for k, v in self.metadata.items()}
        metadata_array = np.array(metadata)
        # how to save the metadata here???
        np.save(file_, self.data)

    @staticmethod
    def filename(basename):
        return basename + '.npy'


global_artifact_registry.register(artifact_class=NumpyArrayArtifactMmap, data_class=np.ndarray, format='npy_mmap')
