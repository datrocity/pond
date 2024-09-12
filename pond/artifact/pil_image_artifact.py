from matplotlib.pyplot import Figure
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from pond.artifact import Artifact
from pond.artifact.artifact_registry import global_artifact_registry


def _image_from_matplotlib_fig(fig):
    """ Transform a Matplotlib Figure in a PIL RGB Image object"""
    fig.canvas.draw()
    image = Image.frombytes(
        'RGB',
        fig.canvas.get_width_height(),
        fig.canvas.tostring_rgb()
    )
    return image


class PILImageArtifact(Artifact):
    """ Artifact for Matlab figures.
    """

    def __init__(self, data, metadata=None, data_hash=None):
        """ Create an Artifact.

        Parameters
        ----------
        data: Image | Figure
            A PIL Image or Matplotlib Figure object.
            A Matplotlib Figure is going to be transformed in an Image.
        metadata: dict
            User-defined metadata, saved with the artifact (optional).
            The metadata keys and values will be stored as strings.
        data_hash: str
            The data hash of the data, if known (for example, when the artifact
            is read from a Version). If None, the hash is re-computed.
        """
        # Transform the matplotlib figure in a PNG image.
        if isinstance(data, Figure):
            data = _image_from_matplotlib_fig(data)
        super().__init__(data, metadata, data_hash=data_hash)

    # --- Artifact class interface

    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        """ Read a Matlab figure artifact from CSV file. """
        # todo "copy" is because opening the file is lazy; is there a better way?
        image = Image.open(file_).copy()
        metadata = image.info
        return image, metadata

    @staticmethod
    def filename(basename):
        return basename + '.png'

    # --- Artifact interface

    def write_bytes(self, file_, **kwargs):
        png_metadata = PngInfo()
        for key, value in self.metadata.items():
            png_metadata.add_text(key, str(value))

        self.data.save(file_, pnginfo=png_metadata)


global_artifact_registry.register(artifact_class=PILImageArtifact, data_class=Image, format='png')
global_artifact_registry.register(artifact_class=PILImageArtifact, data_class=Figure,
                                  format='png')
