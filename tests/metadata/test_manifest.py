import pytest

from pond.metadata.manifest import Manifest
from pond.storage.file_datastore import FileDatastore


@pytest.fixture
def nested_metadata():
    user_metadata = {'a': '2', 'b': 'c'}
    sys_metadata = {'foo': 'bar'}
    dict_ = {
        'user': user_metadata,
        'sys': sys_metadata,
    }
    return dict_


def test_from_nested_dict(nested_metadata):
    manifest = Manifest.from_nested_dict(nested_metadata)
    assert manifest.collect() == nested_metadata


def test_to_form_yaml(tmp_path, nested_metadata):
    manifest = Manifest.from_nested_dict(nested_metadata)

    datastore = FileDatastore(id='foostore', base_path=str(tmp_path))
    manifest_location = tmp_path / 'test.yml'
    manifest.to_yaml(manifest_location, datastore)

    reloaded = Manifest.from_yaml(manifest_location, datastore)
    assert reloaded.collect() == nested_metadata

