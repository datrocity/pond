from matplotlib.pyplot import Figure
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from pond.artifact import Artifact
from pond.artifact.artifact_registry import global_artifact_registry


class PILImageArtifact(Artifact):
    """ Artifact for Matlab figures.
    """

    # --- Artifact class interface

    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        """ Read a Matlab figure artifact from CSV file. """
        # todo "copy" is because opening the file is lazy; is there a better way?
        image = Image.open(file_).copy()
        metadata = image.info
        return cls(image, metadata)

    @staticmethod
    def filename(basename):
        return basename + '.png'

    # --- PILImageArtifact class interface

    @classmethod
    def from_matplotlib_fig(cls, fig, metadata=None):
        fig.canvas.draw()
        image = Image.frombytes(
            'RGB',
            fig.canvas.get_width_height(),
            fig.canvas.tostring_rgb()
        )
        return cls(image, metadata)

    # --- Artifact interface

    def write_bytes(self, file_, **kwargs):
        png_metadata = PngInfo()
        for key, value in self.metadata.items():
            png_metadata.add_text(key, str(value))

        self.data.save(file_, pnginfo=png_metadata)


class MatplotlibFigureArtifact(Artifact):

    # --- Artifact class interface

    # TODO: this can't return another class
    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        """ Read a Matlab figure artifact from CSV file. """
        image = Image.open(file_).copy()
        metadata = image.info
        return PILImageArtifact(image, metadata)

    @staticmethod
    def filename(basename):
        return basename + '.png'

    def write_bytes(self, file_, **kwargs):
        pil = PILImageArtifact.from_matplotlib_fig(self.data, self.metadata)
        pil.write_bytes(file_, **kwargs)


global_artifact_registry.register(artifact_class=PILImageArtifact, data_class=Image, format='png')
global_artifact_registry.register(artifact_class=MatplotlibFigureArtifact, data_class=Figure,
                                  format='png')
