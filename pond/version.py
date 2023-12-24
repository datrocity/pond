import datetime
from typing import Optional

from pond.artifact import Artifact
from pond.conventions import (
    version_data_location,
    version_location,
    version_manifest_location,
    version_uri,
)
from pond.exceptions import VersionDoesNotExist
from pond.metadata.dict import DictMetadataSource
from pond.metadata.manifest import Manifest
from pond.storage.datastore import Datastore
from pond.version_name import VersionName


class Version:

    def __init__(self, artifact_name: str, version_name: VersionName, artifact: Artifact,
                 manifest: Optional[Manifest] = None):
        """ Manages a version: its manifest, name, and artifact.
        """
        self.artifact_name = artifact_name
        self.version_name = version_name
        self.manifest = manifest
        self.artifact = artifact

    def get_metadata(self, location, datastore, data_filename):
        version_metadata = {
            'uri': self.get_uri(location, datastore),
            'filename': data_filename,
            'date_time': datetime.datetime.now(),
            'artifact_name': self.artifact_name,
        }
        version_metadata_source = DictMetadataSource(name='version', metadata=version_metadata)
        return version_metadata_source

    def write(self, location: str, datastore: Datastore, manifest: Manifest):
        # TODO: manifest is modified in-place, is that an issue?

        #: location of the version folder
        version_location_ = version_location(location, self.version_name)
        #: location of the manifest file
        manifest_location = version_manifest_location(version_location_)

        #: filename for the saved data
        data_basename = f'{self.artifact_name}_{str(self.version_name)}'
        data_filename = self.artifact.filename(data_basename)

        version_metadata_source = self.get_metadata(location, datastore, data_filename)
        manifest.add_section(version_metadata_source)
        artifact_metadata_source = self.artifact.get_artifact_metadata()
        manifest.add_section(artifact_metadata_source)
        manifest.to_yaml(manifest_location, datastore)

        datastore.makedirs(version_location_)
        data_location = version_data_location(version_location_, data_filename)
        with datastore.open(data_location, 'wb') as f:
            self.artifact.write_bytes(f)

        # save stored manifest
        self.manifest = manifest

    # todo store and recover artifact_class from manifest
    @classmethod
    def read(cls, version_name, artifact_class, location, datastore):
        #: location of the version folder
        version_location_ = version_location(location, version_name)
        #: location of the manifest file
        manifest_location = version_manifest_location(version_location_)

        if not datastore.exists(manifest_location):
            raise VersionDoesNotExist(location, str(version_name))
        manifest = Manifest.from_yaml(manifest_location, datastore)

        version_metadata = manifest.collect_section('version')
        data_filename = version_metadata['filename']
        data_location = version_data_location(version_location_, data_filename)
        user_metadata = manifest.collect_section('user')
        with datastore.open(data_location, 'rb') as f:
            artifact = artifact_class.read_bytes(f, metadata=user_metadata)

        version = cls(
            artifact_name=version_metadata['artifact_name'],
            version_name=version_name,
            artifact=artifact,
            manifest=manifest,
        )

        return version

    def get_uri(self, location, datastore):
        """ Build URI for a specific location and datastore. """
        uri = version_uri(datastore.id, location, self.artifact_name, self.version_name)
        return uri

    def exists(self, location: str, datastore: Datastore):
        """ Does this version already exists on disk?

        Parameters
        ----------
        location: str
            Root location in the data store where artifacts are read/written. This is used to
            create folder-like groups inside a datastore. This can be, for instance, the name of
            a project or experiment.
        datastore: Datastore
            Data store object, representing the location where the artifacts are read/written.
        """
        #: location of the version folder
        version_location_ = version_location(location, self.version_name)
        #: location of the manifest file
        manifest_location = version_manifest_location(version_location_)

        return datastore.exists(manifest_location)
