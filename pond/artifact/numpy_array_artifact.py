import numpy as np

from pond.artifact import Artifact
from pond.artifact.artifact_registry import global_artifact_registry


class NumpyArrayArtifact(Artifact):
    """ Artifact for numpy arrays.

    The array is saved in .npy format. This format does not allow for saving metadata inside the artifact data file.
    If you want to save the metadata together with the file, refer to the `NumpyArrayCompressedArtifact` artifact
    class.

    The artifact data can be read in "memmap" read mode, which allows accessing the numpy array using the usual
    array interface, while keeping the data on disk. Refer to the `numpy.memmap` documentation for more information.
    """

    @classmethod
    def _read_bytes(cls, file_, memmap=False):
        """ Read a numpy array from a npy binary file. """

        if memmap:
            mmap_mode = 'r'
        else:
            mmap_mode = None
        data = np.load(file_.name, allow_pickle=True, mmap_mode=mmap_mode)
        metadata = None

        return data, metadata

    def write_bytes(self, file_):
        np.save(file_, self.data)

    @staticmethod
    def filename(basename):
        return basename + '.npy'


class NumpyArrayCompressedArtifact(Artifact):
    """ Artifact for numpy arrays.

    The array is saved in .npz format. This format allows to store numpy arrays without installing an additional
    dependency, and to include the metadata as an additional array in the file itself.
    """

    @classmethod
    def _read_bytes(cls, file_):
        """ Read a numpy array from a npy binary file. """
        content = np.load(file_, allow_pickle=True)
        data = content['data']
        metadata = content['metadata'][()]
        return data, metadata

    def write_bytes(self, file_):
        # The pond convention is that all stored metadata is a string
        metadata = {k: str(v) for k, v in self.metadata.items()}
        metadata_array = np.array(metadata)
        np.savez_compressed(file_, data=self.data, metadata=metadata_array)

    @staticmethod
    def filename(basename):
        return basename + '.npz'


global_artifact_registry.register(artifact_class=NumpyArrayArtifact, data_class=np.ndarray, format='npy')
global_artifact_registry.register(artifact_class=NumpyArrayCompressedArtifact, data_class=np.ndarray, format='npz')
