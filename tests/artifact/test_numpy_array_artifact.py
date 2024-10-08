import numpy as np
from numpy.testing import assert_almost_equal
import pytest

from pond.artifact.numpy_array_artifact import NumpyArrayArtifact


@pytest.fixture
def np_array():
    data = np.array(
        [[1.2, 3.1, 7.4],
         [np.nan, 1.0, np.nan]],
    )
    return data


@pytest.fixture
def metadata():
    metadata = {
        'source': 'test_to_csv_stream a b',
        'm1': 12.3,
    }
    return metadata


def test_write_then_read(tmp_path, np_array, metadata):
    artifact = NumpyArrayArtifact(np_array, metadata)
    filename = NumpyArrayArtifact.filename('test')
    path = tmp_path / filename

    artifact.write(path)
    assert path.exists()

    with open(path, 'rb') as f:
        content = NumpyArrayArtifact.read_bytes(f)
    assert_almost_equal(np_array, content.data)
    assert content.metadata == {k: str(v) for k, v in artifact.metadata.items()}


def test_data_hash():
    data1 = np.array([1, 2, 3])
    artifact1 = NumpyArrayArtifact(data1)

    data2 = np.array([1, 2, 3])
    artifact2 = NumpyArrayArtifact(data2)

    data3 = np.array([4, 5, 6])
    artifact3 = NumpyArrayArtifact(data3)

    assert artifact1.data_hash == artifact2.data_hash
    assert artifact1.data_hash != artifact3.data_hash
