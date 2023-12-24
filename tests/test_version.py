from datetime import datetime

import pandas as pd
import pytest

from pond.artifact.pandas_dataframe_artifact import PandasDataFrameArtifact
from pond.exceptions import VersionDoesNotExist
from pond.metadata.metadata_source import MetadataSource
from pond.metadata.manifest import Manifest
from pond.storage.file_datastore import FileDatastore
import pond.version
from pond.version import Version
from pond.version_name import SimpleVersionName


def mock_datetime_now(module, date_time_now, monkeypatch):
    class MockDatetime(datetime):
        @classmethod
        def now(cls):
            return date_time_now
    monkeypatch.setattr(module, "datetime", MockDatetime)


def test_write_then_read(tmp_path):
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    user_metadata = {'a': 'b', 'c': 11}
    artifact_name = 'meh'
    version = Version(
        artifact_name=artifact_name,
        version_name=SimpleVersionName(version_number=42),
        artifact=PandasDataFrameArtifact(data=data),
    )
    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    manifest = Manifest.from_nested_dict({'user': user_metadata})

    assert version.manifest is None
    version.write(location='abc', datastore=store, manifest=manifest)
    saved_manifest = version.manifest.collect()
    assert 'user' in saved_manifest
    assert 'version' in saved_manifest

    assert store.exists('abc/v42')
    assert store.exists('abc/v42/meh_v42.csv')
    assert store.exists('abc/v42/_pond/manifest.yml')

    reloaded_version = Version.read(
        version_name=SimpleVersionName(version_number=42),
        artifact_class=PandasDataFrameArtifact,
        location='abc',
        datastore=store,
    )

    # Reloaded artifact has got the user metadata
    reloaded_artifact = reloaded_version.artifact
    pd.testing.assert_frame_equal(reloaded_artifact.data, data)
    expected_user_metadata = {k: str(v) for k, v in user_metadata.items()}
    assert reloaded_artifact.metadata == expected_user_metadata

    # Reloaded version has got a manifest with user metadata
    assert reloaded_version.artifact_name == artifact_name
    assert reloaded_version.manifest.collect_section('user') == expected_user_metadata

    # Reloaded version has got a manifest with version metadata
    reloaded_version_metadata = reloaded_version.manifest.collect_section('version')
    assert reloaded_version_metadata['artifact_name'] == artifact_name
    assert reloaded_version_metadata['filename'] == 'meh_v42.csv'
    assert reloaded_version_metadata['uri'] == 'pond://foostore/abc/meh/v42'
    assert 'date_time' in reloaded_version_metadata


def test_version_uri(tmp_path):
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    version_name = SimpleVersionName(version_number=42)
    version = Version(
        artifact_name='foo',
        version_name=version_name,
        artifact=PandasDataFrameArtifact(data=data),
        manifest=None,
    )
    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    uri = version.get_uri(location='exp1', datastore=store)
    assert uri == 'pond://foostore/exp1/foo/v42'


def test_version_metadata(tmp_path, monkeypatch):
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    version_name = SimpleVersionName(version_number=42)
    version = Version(
        artifact_name='foo',
        version_name=version_name,
        artifact=PandasDataFrameArtifact(data=data),
        manifest=None,
    )

    date_time_now = datetime(2020, 12, 25, 17, 5, 55)
    mock_datetime_now(pond.version.datetime, date_time_now, monkeypatch)

    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    data_filename = 'foo.csv'

    metadata_source = version.get_metadata('exp1', store, data_filename)

    assert isinstance(metadata_source, MetadataSource)
    assert metadata_source.name == 'version'
    metadata = metadata_source.collect()
    assert metadata['filename'] == data_filename
    assert metadata['uri'] == 'pond://foostore/exp1/foo/v42'
    assert metadata['date_time'] == str(date_time_now)


def test_exists(tmp_path):
    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    location = 'abc'

    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    version_name = SimpleVersionName(version_number=42)
    version = Version(
        artifact_name='foo',
        version_name=version_name,
        artifact=PandasDataFrameArtifact(data=data),
    )

    assert not version.exists(location, store)

    version.write(location=location, datastore=store, manifest=Manifest())

    assert version.exists(location, store)


def test_read_not_existing(tmp_path):
    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    location = 'abc'
    with pytest.raises(VersionDoesNotExist):
        Version.read(
            version_name='v1',
            artifact_class=PandasDataFrameArtifact,
            location=location,
            datastore=store,
        )
