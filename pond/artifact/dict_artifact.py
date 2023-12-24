import json

from pond.artifact import Artifact
from pond.conventions import TXT_ENCODING


class DictArtifact(Artifact):
    """ Artifact for dictionaries.

    A typical use for this artifact is to save the parameters of experiments.
    """

    @staticmethod
    def filename(basename):
        return basename + '.json'

    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        txt = file_.read().decode()
        data = json.loads(txt)
        metadata = data.pop('__metadata__', dict())
        return cls(data, metadata)

    def write_bytes(self, file_, **kwargs):
        dict_ = dict(self.data)
        dict_['__metadata__'] = {str(k): str(v) for k, v in self.metadata.items()}
        txt = json.dumps(dict_)
        file_.write(str.encode(txt, TXT_ENCODING))
