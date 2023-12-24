import json
import logging
import time
from typing import List, Type, Optional, Union

from pond.artifact import Artifact
from pond.conventions import (
    DataType,
    WriteMode,
    version_manifest_location,
    version_location,
    versions_lock_file_location,
    versioned_artifact_location,
)
from pond.exceptions import (
    IncompatibleVersionName, VersionAlreadyExists,
)
from pond.metadata.manifest import Manifest
from pond.storage.datastore import Datastore
from pond.version import Version
from pond.version_name import VersionName


logger = logging.getLogger(__name__)

# Time to wait before retrying when creating a new version fails
NEW_VERSION_WAIT_MS = 1000


class VersionedArtifact:

    def __init__(self,
                 artifact_name: str,
                 location: str,
                 datastore: Datastore,
                 artifact_class: Type[Artifact],
                 version_name_class: Type[VersionName]):
        """ An artifact versioned and stored on disk.

        `VersionedArtifact` manages the versioning, data, and metadata, of an artifact.

        Parameters
        ----------
        artifact_name: str
            Name of the artifact.
        location: str
            Root location in the data store where artifacts are read/written. This is used to
            create folder-like groups inside a datastore. This can be, for instance, the name of
            a project or experiment.
        datastore: Datastore
            Data store object, representing the storage where the artifacts are read/written.
        artifact_class: Type[Artifact]
        version_name_class: Type[VersionName]
            Class used to create increasing version names. The default value,
            `SimpleVersionName` creates version names as `v1`, `v2`, etc.
        """
        self.artifact_name = artifact_name
        self.location = location
        self.datastore = datastore
        self.artifact_class = artifact_class
        self.version_name_class = version_name_class

        self.versions_manifest = {
            'artifact_class': artifact_class.class_id(),
            'version_name_class': version_name_class.class_id(),
        }

        self.versions_location = versioned_artifact_location(location, artifact_name)
        # todo this goes to conventions.py
        self.versions_list_location = f'{self.versions_location}/versions.json'
        self.versions_manifest_location = f'{self.versions_location}/manifest.yml'

        if not self.datastore.exists(self.versions_location):
            # Create the versioned artifact folder organization if it does not exist
            self.datastore.makedirs(self.versions_location)
            self._write_version_names([])
            self.versions_manifest['artifact_class'] = artifact_class.class_id()
            self.versions_manifest['version_name_class'] = version_name_class.class_id()
            self._write_manifest()

    # --- VersionedArtifact class interface

    @classmethod
    def from_datastore(cls, artifact_name: str, location: str, datastore: Datastore):
        versions_location = versioned_artifact_location(location, artifact_name)
        versions_manifest_location = f'{versions_location}/manifest.yml'
        versions_manifest = datastore.read_yaml(versions_manifest_location)

        artifact_class_id = versions_manifest['artifact_class']
        artifact_class = Artifact.subclass_from_id(artifact_class_id)
        version_name_class_id = versions_manifest['version_name_class']
        version_name_class = VersionName.subclass_from_id(version_name_class_id)

        versioned_artifact = cls(
            artifact_name=artifact_name,
            location=location,
            datastore=datastore,
            artifact_class=artifact_class,
            version_name_class=version_name_class,
        )
        return versioned_artifact

    # --- VersionedArtifact public interface

    def read(self, version_name: Optional[Union[str, VersionName]] = None) -> Version:
        """ Read a version of the artifact.

        Parameters
        ----------
        version_name: Union[str, VersionName], optional
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.

        Raises
        ------
        VersionDoesNotExist
            If the requested version does not exist.

        Returns
        -------
        Version
            The version object read from storage.
        """

        if version_name is not None:
            if isinstance(version_name, str):
                version_name = self.version_name_class.from_string(version_name)
        else:
            version_name = self.latest_version_name()

        version = Version.read(
            version_name=version_name,
            artifact_class=self.artifact_class,
            datastore=self.datastore,
            location=self.versions_location,
        )

        return version

    def write(self,
              data: DataType,
              manifest: Manifest,
              version_name: Optional[Union[str, VersionName]] = None,
              write_mode: WriteMode = WriteMode.ERROR_IF_EXISTS):
        """ Write some data to storage.

        Parameters
        ----------
        data: DataType
            The artifact data to write.
        manifest: Manifest
            Metadata to store with the data.
        version_name: Union[str, VersionName], optional
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.
        write_mode: WriteMode
            Write mode, either WriteMode.ERROR_IF_EXISTS or WriteMode.OVERWRITE.

        Raises
        ------
        IncompatibleVersionName
            If the provided version name does not correspond to the version name class used in
            this versioned artifact.
        VersionAlreadyExists
            If the provided version name exists, and the write mode is "ERROR_IF_EXISTS".

        Returns
        -------
        Version
            The version object read from storage.
        """
        # todo lock

        if version_name is None:
            prev_version_name = self.latest_version_name(raise_if_none=False)
            version_name = self.version_name_class.next(prev_version_name)

        if isinstance(version_name, str):
            version_name = VersionName.from_string(version_name)

        if not isinstance(version_name, self.version_name_class):
            raise IncompatibleVersionName(
                version_name=version_name,
                version_name_class=self.version_name_class,
            )

        user_metadata = manifest.collect_section('user', default_metadata={})
        artifact = self.artifact_class(data, metadata=user_metadata)
        version = Version(self.artifact_name, version_name, artifact)

        if version.exists(self.versions_location, self.datastore):
            if write_mode == WriteMode.ERROR_IF_EXISTS:
                uri = version.get_uri(self.location, self.datastore)
                raise VersionAlreadyExists(uri)
            elif write_mode == WriteMode.OVERWRITE:
                uri = version.get_uri(self.location, self.datastore)
                logger.info(f"Deleting existing version before overwriting: {uri}")
                version_location_ = version_location(self.versions_location, version_name)
                self.datastore.delete(version_location_, recursive=True)

        version.write(self.versions_location, self.datastore, manifest)
        self._register_version_name(version_name)

        return version

    def all_version_names(self) -> List[VersionName]:
        """Get all locked (and existing) artifact version names.

        Locked versions might not be existing yet, they are just reserved names.

        Returns
        -------
        List[VersionName]
            A list of all locked version names
        """
        try:
            raw_versions = json.loads(self.datastore.read(self.versions_list_location))
        except FileNotFoundError:
            raw_versions = []
        versions = [VersionName.from_string(raw_version) for raw_version in list(raw_versions)]
        return sorted(versions)

    def version_names(self) -> List[VersionName]:
        """Get all existing artifact version names.

        Versions are considered as "existing" as soon as they have a "manifest.yml"

        Returns
        -------
        List[VersionName]
            A list of all existing version names
        """
        # todo create version_exists
        return [
            name for name in self.all_version_names()
            if self.datastore.exists(
                version_manifest_location(
                    version_location(self.versions_location, name)
                )
            )
        ]

    def latest_version_name(self, raise_if_none=True) -> VersionName:
        """Get the name of the latest version. If none is defined, will raise an exception

        Raises
        ------
        ArtifactHasNoVersion
            If the artifact has no latest version

        Returns
        -------
        VersionName
            The name of the latest version
        """
        versions = self.version_names()
        if not versions:
            if raise_if_none:
                raise ArtifactHasNoVersion(self.location)
            else:
                return None
        return versions[-1]

    def latest_version(self) -> Version:
        """Get the latest version. If none is defined, will raise an exception

        Raises
        ------
        TableHasNoVersion
            If the artifact has no latest version

        Returns
        -------
        Version
            The latest version of this artifact
        """
        return self.read(self.latest_version_name())

    # TODO: TEST
    def delete_version(self, version_name: Union[str, VersionName]) -> None:
        """Delete a version, will not fail if the version did not exist

        Parameters
        ----------
        version_name: Union[str, VersionName]
            Name of the version to delete
        """
        if not isinstance(version_name, VersionName):
            version_name = VersionName.from_string(version_name)

        self.datastore.delete(version_location(self.location, version_name), recursive=True)

        # todo: need to lock versions.json here
        names = self.all_version_names()
        if version_name in names:
            names.remove(version_name)
        self._write_version_names(names)
        # todo: need to unlock versions.json here

    # --- VersionedArtifact private interface

    def _create_version_name(self, retry: bool = True) -> VersionName:
        versions_lock_file = versions_lock_file_location(self.location)
        if self.datastore.exists(versions_lock_file):
            # In case another process just created the data dir and did non update yet the versions
            # list, let's wait a little and retry once
            if retry:
                time.sleep(NEW_VERSION_WAIT_MS / 1000)
                return self._create_version_name(False)
            else:
                raise ArtifactVersionsIsLocked(self.location)
        # todo: this is not safe in case of concurrency.
        self.datastore.write_string(versions_lock_file, '')
        try:
            names = self.all_version_names()
            name = names[-1].next() if names else FIRST_VERSION_NAME
            new_version_name = self._register_version_name(name)
        finally:
            self.datastore.delete(versions_lock_file)

        return new_version_name

    def _register_version_name(self, name: VersionName) -> VersionName:
        # todo: need to lock versions.json here
        names = self.all_version_names()

        if name not in names:
            names.append(name)
            self._write_version_names(names)
            # todo: need to unlock versions.json here

        return name

    def _write_version_names(self, names: List[VersionName]) -> None:
        """Sort, serialize and write version names"""
        strings = [str(name) for name in sorted(names)]
        self.datastore.write_json(self.versions_list_location, strings)

    def _write_manifest(self):
        self.datastore.write_yaml(self.versions_manifest_location, self.versions_manifest)

    def _read_manifest(self):
        return self.datastore.read_yaml(self.versions_manifest_location)
