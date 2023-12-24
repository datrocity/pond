import pandas as pd

from pond.artifact import Artifact
from pond.artifact.artifact_registry import global_artifact_registry
from pond.conventions import TXT_ENCODING


class PandasDataFrameArtifact(Artifact):
    """ Artifact for Pandas DataFrames.
    """

    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        """ Read a Pandas DataFrame artifact from CSV file.

        By default, the first column in the file is used as the index. This can be changed using
        the `index_col` keyword argument.
        """
        metadata = {}
        while file_.read(1) == b'#':
            line = file_.readline().decode()
            key, value = line.strip().split(' ', 1)
            metadata[key] = value
        file_.seek(0)

        # We want to read the index from the first column by default, but it can be overwritten
        kwargs.setdefault('index_col', 0)
        data = pd.read_csv(file_, comment='#', **kwargs)
        return cls(data, metadata)

    def write_bytes(self, file_, **kwargs):
        for key, value in self.metadata.items():
            txt = f'# {key} {value}\n'
            file_.write(str.encode(txt, TXT_ENCODING))
        self.data.to_csv(file_, **kwargs)

    @staticmethod
    def filename(basename):
        return basename + '.csv'


global_artifact_registry.register(artifact_class=PandasDataFrameArtifact, data_class=pd.DataFrame, format='csv')
