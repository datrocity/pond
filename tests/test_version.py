from datetime import datetime

import pandas as pd
import pytest

from pond.artifact import Artifact
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


def test_read_manifest(tmp_path):
    # Write a version, so that we can read its manifest later
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    user_metadata = {'a': 'b', 'c': 11}
    artifact_name = 'meh'
    version = Version(
        artifact_name=artifact_name,
        version_name=SimpleVersionName(version_number=42),
        artifact=PandasDataFrameArtifact(data=data),
    )
    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    user_manifest = Manifest.from_nested_dict({'user': user_metadata})
    version.write(location='abc', datastore=store, manifest=user_manifest)
    saved_manifest = version.manifest.collect()

    manifest = Version.read_manifest(
        version_name=SimpleVersionName(version_number=42),
        location='abc',
        datastore=store,
    )
    reloaded_manifest = manifest.collect()

    assert reloaded_manifest == saved_manifest


def test_read_manifest_not_existing(tmp_path):
    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    location = 'abc'
    with pytest.raises(VersionDoesNotExist):
        Version.read_manifest(
            version_name='v1',
            location=location,
            datastore=store,
        )


def test_data_hash_not_recomputed_on_read(tmp_path, monkeypatch):
    # The data hash should not be recomputed when re-reading a version
    data = pd.DataFrame([[1, 2]], columns=['c1', 'c2'])
    artifact_name = 'meh'
    version = Version(
        artifact_name=artifact_name,
        version_name=SimpleVersionName(version_number=42),
        artifact=PandasDataFrameArtifact(data=data),
    )
    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    manifest = Manifest.from_nested_dict({})
    version.write(location='abc', datastore=store, manifest=manifest)
    expected_data_hash = version.manifest.collect_section('artifact')['data_hash']

    # If Artifact._data_hash is called, we get an exception
    def _data_hash_bomb(self):
        raise RuntimeError("you should not be here")
    monkeypatch.setattr(pond.artifact.Artifact, "_data_hash", _data_hash_bomb)

    try:
        reloaded_version = Version.read(
            version_name=SimpleVersionName(version_number=42),
            artifact_class=PandasDataFrameArtifact,
            location='abc',
            datastore=store,
        )
    except RuntimeError:
        pytest.fail("_data_hash_was_called")
    reloaded_data_hash = reloaded_version.manifest.collect_section('artifact')['data_hash']
    assert reloaded_data_hash == expected_data_hash


class MockArtifactWithNoMetadata(Artifact):

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

    def get_artifact_metadata(self):
        # Do not return artifact metadata, as in older versions
        return None


def test_artifact_section_not_in_manifest_on_read(tmp_path):
    # Reproduces issue https://github.com/datrocity/pond/issues/25
    # Allow backwards compatibility for the data saved on older versions of pond,
    # when the manifest did not have an "artifact" section
    data = [1, 2, 3]
    artifact_name = 'meh'
    version = Version(
        artifact_name=artifact_name,
        version_name=SimpleVersionName(version_number=42),
        artifact=MockArtifactWithNoMetadata(data=data),
    )
    store = FileDatastore(id='foostore', base_path=str(tmp_path))
    manifest = Manifest.from_nested_dict({})
    version.write(location='abc', datastore=store, manifest=manifest)

    reloaded_version = Version.read(
        version_name=SimpleVersionName(version_number=42),
        artifact_class=MockArtifactWithNoMetadata,
        location='abc',
        datastore=store,
    )
    # The "artifact" section was not saved
    assert 'artifact' not in reloaded_version.manifest.collect()
    # The data hash is computed on the fly, nevertheless
    assert reloaded_version.artifact.data_hash is not None
