from pond.artifact import Artifact


class MockArtifact(Artifact):
    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        artifact = MockArtifact(data=[], metadata={})
        artifact.filename = file_.name
        artifact.read_kwargs = kwargs
        return artifact

    def write_bytes(self, file_, **kwargs):
        self.filename = file_.name
        self.write_kwargs = kwargs

    @staticmethod
    def filename(basename):
        return basename


def test_read(tmp_path):
    kwargs = {'c': 3}
    path = str(tmp_path / "filename.ext")
    with open(path, 'wb') as f:
        f.write(b'abc')

    artifact = MockArtifact.read(path, **kwargs)
    # check that read_bytes has been called with the right arguments
    assert artifact.filename == path
    assert artifact.read_kwargs == kwargs


def test_read_with_external_metadata(tmp_path):
    path = str(tmp_path / "filename.ext")
    with open(path, 'wb') as f:
        f.write(b'abc')

    external_metadata = {'blah': 4}
    artifact = MockArtifact.read(path, metadata=external_metadata)
    # check that read_bytes has been called with the right arguments
    assert artifact.filename == path
    assert artifact.metadata == external_metadata


def test_write(tmp_path):
    data = [1, 2, 3]
    metadata = {'a': 'b'}
    artifact = MockArtifact(data, metadata)

    kwargs = {'c': 3}
    path = str(tmp_path / "filename.ext")
    artifact.write(path, **kwargs)
    # check that write_bytes has been  called with the right arguments
    assert artifact.filename == path
    assert artifact.write_kwargs == kwargs
