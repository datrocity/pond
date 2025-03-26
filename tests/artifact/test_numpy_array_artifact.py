import numpy as np
from numpy.testing import assert_almost_equal
import pytest

from pond import Activity
from pond.artifact.artifact_registry import global_artifact_registry
from pond.artifact.numpy_array_artifact import NumpyArrayArtifact, NumpyArrayCompressedArtifact
from pond.storage.file_datastore import FileDatastore


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


def test_fetch_from_global_registry(tmp_path, np_array):
    array_artifacts = global_artifact_registry.get_available_artifacts(data_class=np_array.__class__)
    assert len(array_artifacts) >= 1
    all_artifact_types = [artifact.artifact_class for artifact in array_artifacts]
    assert NumpyArrayArtifact in all_artifact_types
    assert NumpyArrayCompressedArtifact in all_artifact_types
    # We want the version with metadata to be preferred, and so be registered later.
    assert all_artifact_types.index(NumpyArrayArtifact) < all_artifact_types.index(NumpyArrayCompressedArtifact)


def test_npz_write_then_read(tmp_path, np_array, metadata):
    artifact = NumpyArrayCompressedArtifact(np_array, metadata)
    filename = NumpyArrayCompressedArtifact.filename('test')
    path = tmp_path / filename

    artifact.write(path)
    assert path.exists()

    with open(path, 'rb') as f:
        content = NumpyArrayCompressedArtifact.read_bytes(f)
    assert_almost_equal(np_array, content.data)
    assert content.metadata == {k: str(v) for k, v in artifact.metadata.items()}


def test_npz_data_hash():
    data1 = np.array([1, 2, 3])
    artifact1 = NumpyArrayCompressedArtifact(data1)

    data2 = np.array([1, 2, 3])
    artifact2 = NumpyArrayCompressedArtifact(data2)

    data3 = np.array([4, 5, 6])
    artifact3 = NumpyArrayCompressedArtifact(data3)

    assert artifact1.data_hash == artifact2.data_hash
    assert artifact1.data_hash != artifact3.data_hash


def test_npy_write_then_read(tmp_path, np_array):
    artifact = NumpyArrayArtifact(np_array)
    filename = NumpyArrayArtifact.filename('test')
    path = tmp_path / filename

    artifact.write(path)
    assert path.exists()

    # Read in memory
    with open(path, 'rb') as f:
        content = NumpyArrayArtifact.read_bytes(f)
    assert_almost_equal(np_array, content.data)
    assert not isinstance(content.data, np.memmap)

    # Read as a memmap
    with open(path, 'rb') as f:
        content = NumpyArrayArtifact.read_bytes(f, memmap=True)
    assert_almost_equal(np_array, content.data)
    # Check that it's a read-only memmap
    assert isinstance(content.data, np.memmap)
    assert content.data.mode == 'r'


def test_npz_data_hash():
    data1 = np.array([1, 2, 3])
    artifact1 = NumpyArrayArtifact(data1)

    data2 = np.array([1, 2, 3])
    artifact2 = NumpyArrayArtifact(data2)

    data3 = np.array([4, 5, 6])
    artifact3 = NumpyArrayArtifact(data3)

    assert artifact1.data_hash == artifact2.data_hash
    assert artifact1.data_hash != artifact3.data_hash


def test_read_memmap_from_activity(tmp_path, np_array):
    datastore = FileDatastore(id='foostore', base_path=tmp_path)
    activity = Activity(
        source='test_pond.py',
        datastore=datastore,
        location='test_location',
    )

    activity.write(np_array, 'foo')
    foo = activity.read('foo', memmap=True)

    assert_almost_equal(np_array, foo)
