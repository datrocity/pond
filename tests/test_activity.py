import pytest

from pond import Activity
from pond.artifact import Artifact
from pond.artifact.artifact_registry import ArtifactRegistry
from pond.conventions import WriteMode, versioned_artifact_location
from pond.exceptions import VersionAlreadyExists
from pond.metadata.metadata_source import MetadataSource
from pond.storage.file_datastore import FileDatastore
from pond.version_name import SimpleVersionName


# test: inputs are saved as metadata
# test: pond.write without giving class explicitly


class MockArtifact(Artifact):
    @classmethod
    def _read_bytes(cls, file_, **kwargs):
        data = file_.read().decode()
        return cls(data=data)

    def write_bytes(self, file_, **kwargs):
        file_.write(str.encode(self.data))

    @staticmethod
    def filename(basename):
        return basename + '.mock'


@pytest.fixture
def activity(tmp_path):
    datastore = FileDatastore(id='foostore', base_path=tmp_path)
    activity = Activity(
        source='test_pond.py',
        datastore=datastore,
        location='test_location',
        author='John Doe',
        version_name_class=SimpleVersionName,
    )
    return activity


def test_pond_write_then_read_version_explicit(activity):
    """ Can write and read artifacts when explicitly giving the artifact class. """

    datastore = activity.datastore
    location = activity.location

    # Save first version of the data
    data = 'test_data'
    metadata = {'test': 'xyz'}
    version = activity.write(data, name='foo', artifact_class=MockArtifact, metadata=metadata)

    first_version_name = SimpleVersionName.first()
    assert version.version_name == first_version_name
    assert version.artifact.metadata['test'] == metadata['test']
    assert datastore.exists(
        versioned_artifact_location(location, 'foo'),
    )
    assert isinstance(version.artifact, MockArtifact)

    # Write second version of the data
    data2 = 'test_data2'
    metadata2 = {'test': 'xyz2'}
    version2 = activity.write(data2, name='foo', artifact_class=MockArtifact, metadata=metadata2)
    assert version2.version_name == SimpleVersionName.next(first_version_name)

    # Read the latest version
    version_reloaded = activity.read_version('foo')
    assert version_reloaded.version_name == version2.version_name
    assert version_reloaded.artifact.data == data2
    assert version_reloaded.artifact.metadata == metadata2

    # Read the first version
    version_reloaded = activity.read_version('foo', version_name='v1')
    assert version_reloaded.version_name == version.version_name
    assert version_reloaded.artifact.data == data
    assert version_reloaded.artifact.metadata == metadata

    assert activity.read_history == {
        version.get_uri(location, datastore),
        version2.get_uri(location, datastore),
    }

    # Read the first version, using a VersionName instance
    version_name = SimpleVersionName(version_number=1)
    version_reloaded = activity.read_version('foo', version_name=version_name)
    assert version_reloaded.version_name == version.version_name
    assert version_reloaded.artifact.data == data
    assert version_reloaded.artifact.metadata == metadata

    # Read history is unchanged because loaded the same data twice
    assert activity.read_history == {
        version.get_uri(location, datastore),
        version2.get_uri(location, datastore),
    }


def test_pond_write_then_read_version_implicit(tmp_path):
    # Can write and read artifacts, finding an appropriate artifact class
    registry = ArtifactRegistry()
    registry.register(artifact_class=MockArtifact, data_class=str)
    datastore = FileDatastore(id='foostore', base_path=tmp_path)
    activity = Activity(
        source='test_pond.py',
        datastore=datastore,
        location='test_location',
        author='John Doe',
        version_name_class=SimpleVersionName,
        artifact_registry=registry,
    )

    # Save data without artifact class
    data = 'test_data'
    metadata = {'test': 'xyz'}
    version = activity.write(data, name='foo', metadata=metadata)
    assert isinstance(version.artifact, MockArtifact)


def test_read_data(activity):
    """ Can read saved data. """
    data = 'test_data'
    metadata = {'test': 'xyz'}
    activity.write(data, name='foo', artifact_class=MockArtifact, metadata=metadata)

    data_reloaded = activity.read('foo', version_name='v1')
    assert data_reloaded == data


def test_read_artifact(activity):
    """ Can read saved artifacts. """
    data = 'test_data'
    metadata = {'test': 'xyz'}
    activity.write(data, name='foo', artifact_class=MockArtifact, metadata=metadata)

    artifact = activity.read_artifact('foo', version_name='v1')
    assert artifact.data == data
    assert artifact.metadata == metadata


def test_activity_metadata():
    author = 'John Doe'
    source = 'test_pond.py'
    activity = Activity(
        source=source,
        datastore=None,
        location='test_location',
        author=author,
    )
    # Mock having read some inputs
    inputs = sorted(['pond://test_location/foo/v1', 'pond://test_location/bar/v3'])
    activity.read_history = inputs

    metadata_source = activity.get_metadata()
    assert isinstance(metadata_source, MetadataSource)
    assert metadata_source.name == 'activity'
    metadata = metadata_source.collect()
    assert metadata['author'] == author
    assert metadata['inputs'] == str(inputs)
    assert metadata['source'] == source


def test_write_inputs_to_metadata(activity):
    activity.write('123', name='meh', artifact_class=MockArtifact)
    activity.write('456', name='bah', artifact_class=MockArtifact)
    activity.write('456', name='bah', artifact_class=MockArtifact)

    meh = activity.read('meh')
    bah_version = activity.read_version('bah')

    activity.write('789', name='uzz', artifact_class=MockArtifact)
    uzz_version = activity.read_version('uzz')
    activity_metadata = uzz_version.manifest.collect_section('activity')

    expected_inputs = ['pond://foostore/test_location/bah/v2',
                       'pond://foostore/test_location/meh/v1']
    # TODO activity manifest should parse inputs list
    #assert activity_metadata['inputs'] == expected_inputs
    assert activity_metadata['inputs'] == str(expected_inputs)


def test_write_mode_error_if_exists(activity):
    activity.write('123', name='meh', artifact_class=MockArtifact, version_name='v1')
    with pytest.raises(VersionAlreadyExists):
        activity.write(
            data='234',
            name='meh',
            artifact_class=MockArtifact,
            version_name='v1',
            write_mode=WriteMode.ERROR_IF_EXISTS,
        )


def test_write_mode_overwrite(activity):
    activity.write('123', name='meh', artifact_class=MockArtifact)

    # No exception is raised when overwriting v1
    activity.write(
        data='234',
        name='meh',
        artifact_class=MockArtifact,
        version_name='v1',
        write_mode=WriteMode.OVERWRITE,
    )
    # v1 has got new data
    artifact = activity.read_artifact(name='meh', version_name='v1')
    assert artifact.data == '234'
