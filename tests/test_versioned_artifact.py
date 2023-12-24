import pytest

from pond.artifact import Artifact
from pond.conventions import WriteMode, version_data_location, version_location
from pond.exceptions import IncompatibleVersionName, VersionAlreadyExists
from pond.metadata.manifest import Manifest
from pond.storage.file_datastore import FileDatastore
from pond.version_name import DateTimeVersionName, SimpleVersionName
from pond.versioned_artifact import VersionedArtifact


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
def versioned_artifact(tmp_path):
    datastore = FileDatastore(id='foostore', base_path=tmp_path)
    versioned_artifact = VersionedArtifact(
        artifact_name='test_artifact',
        location='test_location',
        datastore=datastore,
        artifact_class=MockArtifact,
        version_name_class=SimpleVersionName,
    )
    return versioned_artifact


# pond.write(artifact, artifact_name)
# - use artifact_name to look for a versioned artifact in a given datastore and location
#   - if it doesn't exist, create it; use the artifact.class to create a versioned artifact of
#   that kind
#   - if it does exist, check that the artifact class corresponds to the versioned artifact
#   metadata

# test: all_version_names vs version_names
# test: delete version
# test: write new version with different artifact class -> error

def test_versioned_artifact_write_then_read(versioned_artifact):
    datastore = versioned_artifact.datastore

    # Basic files and directories for the versioned artifact are created when they didn't exist
    assert datastore.exists(versioned_artifact.versions_location)
    assert datastore.exists(versioned_artifact.versions_list_location)
    assert versioned_artifact.version_names() == []

    # Create first version
    data = 'test_data'
    metadata = {'test': 'xyz'}
    manifest = Manifest.from_nested_dict({'user': metadata})
    version = versioned_artifact.write(data=data, manifest=manifest)

    first_version_name = SimpleVersionName.first()
    assert version.version_name == first_version_name

    # Reload the first version
    reloaded_artifact = versioned_artifact.read(version_name=first_version_name)
    assert isinstance(reloaded_artifact.artifact, MockArtifact)
    assert reloaded_artifact.artifact.data == data
    assert reloaded_artifact.artifact.metadata == metadata

    # Create another version
    version2 = versioned_artifact.write(data='data2', manifest=Manifest())
    assert version2.version_name == SimpleVersionName.next(version.version_name)

    # Check version name list
    assert versioned_artifact.version_names() == [first_version_name, version2.version_name]


def test_write_mode_error_if_exists(versioned_artifact):
    versioned_artifact.write(data='123', manifest=Manifest())
    with pytest.raises(VersionAlreadyExists):
        versioned_artifact.write(
            data='234',
            manifest=Manifest(),
            version_name='v1',
            write_mode=WriteMode.ERROR_IF_EXISTS,
        )


def test_write_mode_overwrite(versioned_artifact):
    datastore = versioned_artifact.datastore

    v1 = versioned_artifact.write(data='123', manifest=Manifest())
    v2 = versioned_artifact.write(data='abc', manifest=Manifest())
    assert v2.exists(versioned_artifact.versions_location, datastore)

    # Add an extra file to check that the folder is deleted
    version_location_ = version_location(versioned_artifact.versions_location, v1.version_name)
    data_location = version_data_location(version_location_, 'tobedeleted.txt')
    datastore.write_string(data_location, 'XYZ')
    assert datastore.exists(data_location)

    # No exception is raised when overwriting v1
    versioned_artifact.write(
        data='234',
        manifest=Manifest(),
        version_name='v1',
        write_mode=WriteMode.OVERWRITE,
    )
    # v1 has got new data
    version = versioned_artifact.read('v1')
    assert version.artifact.data == '234'
    # Manually added file is gone (version folder was wiped)
    assert not datastore.exists(data_location)
    # v2 still exists
    assert v2.exists(versioned_artifact.versions_location, datastore)


def test_write_incompatible_version_name_class(versioned_artifact):
    with pytest.raises(IncompatibleVersionName):
        versioned_artifact.write(
            data='123',
            manifest=Manifest(),
            version_name=DateTimeVersionName(),
        )
