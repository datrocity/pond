from pond.artifact import Artifact


class MockArtifact(Artifact):
    @classmethod
    def read_bytes(cls, file_, metadata=None, data_hash=None, **kwargs):
        artifact = super().read_bytes(file_, metadata, data_hash)
        #artifact = MockArtifact(data=[], metadata={})
        artifact.filename = file_.name
        artifact.read_kwargs = kwargs
        return artifact

    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        data = file_.read().decode()
        metadata = {}
        return data, metadata

    def write_bytes(self, file_, **kwargs):
        self.filename = file_.name
        self.write_kwargs = kwargs

    @staticmethod
    def filename(basename):
        return basename


def test_read_bytes(tmp_path):
    kwargs = {'c': 3}
    path = str(tmp_path / "filename.ext")
    with open(path, 'wb') as f:
        f.write(b'abc')

    with open(path, 'rb') as f:
        artifact = MockArtifact.read_bytes(f, **kwargs)

    # check that read_bytes has been called with the right arguments
    assert artifact.filename == path
    assert artifact.read_kwargs == kwargs


def test_read_bytes_with_external_metadata(tmp_path):
    path = str(tmp_path / "filename.ext")
    with open(path, 'wb') as f:
        f.write(b'abc')

    external_metadata = {'blah': 4}
    with open(path, 'rb') as f:
        artifact = MockArtifact.read_bytes(f, metadata=external_metadata)
    # check that read_bytes has been called with the right arguments
    assert artifact.filename == path
    assert artifact.metadata == external_metadata


def test_read_bytes_with_data_hash(tmp_path):
    path = str(tmp_path / "filename.ext")
    with open(path, 'wb') as f:
        f.write(b'abc')

    with open(path, 'rb') as f:
        artifact = MockArtifact.read_bytes(f, data_hash='blah')
    assert artifact.data_hash == 'blah'


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


def test_data_hash(tmp_path):
    data1 = [1, 2, 3]
    artifact1 = MockArtifact(data1)

    data2 = [1, 2, 3]
    artifact2 = MockArtifact(data2)

    data3 = [4, 5, 6]
    artifact3 = MockArtifact(data3)

    assert artifact1.data_hash == artifact2.data_hash
    assert artifact1.data_hash != artifact3.data_hash
