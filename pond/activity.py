from typing import Any, Dict, List, Optional, Set, Type, Union

from pond.artifact import Artifact
from pond.artifact.artifact_registry import ArtifactRegistry, global_artifact_registry
from pond.conventions import DataType, WriteMode
from pond.metadata.metadata_source import MetadataSource
from pond.metadata.dict import DictMetadataSource
from pond.metadata.manifest import Manifest
from pond.storage.datastore import Datastore
from pond.version import Version
from pond.version_name import SimpleVersionName, VersionName
from pond.versioned_artifact import VersionedArtifact


class Activity:

    # TODO: can location have subpaths? e.g. `experiment1/test22`

    def __init__(self,
                 source: str,
                 location: str,
                 datastore: Datastore,
                 write_mode: WriteMode = WriteMode.ERROR_IF_EXISTS,
                 author: str = 'NA',
                 version_name_class: Type[VersionName] = SimpleVersionName,
                 artifact_registry: ArtifactRegistry = global_artifact_registry,
                 ):
        """ Read and write artifacts with lineage and metadata.

        Activity is the main user-facing interface for pond. Most of the usages of `pond` only
        ever interact with an instance of this object.

        Parameters
        ----------
        source: str
            String defining where the read/write operations are made. Often, this is the path of
            a file or notebook, used for lineage tracing.
        location: str
            Root location in the data store where artifacts are read/written. This is used to
            create folder-like groups inside a datastore. This can be, for instance, the name of
            a project or experiment.
        datastore: Datastore
            Data store object, representing the storage where the artifacts are read/written.
        write_mode: WriteMode
            Default write mode for this `Activity` instance. The default mode will be used
            unless one is specified during a write operation. See `pond.conventions.WriteMode` for
            possible values.
        author: str
            Author name/identifier, used as metadata. Default is 'NA'.
        version_name_class: VersionName
            Class used to create increasing version names. The default value,
            `SimpleVersionName` creates version names as `v1`, `v2`, etc.
        artifact_registry: ArtifactRegistry
            Registry object mapping data types and file formats to an artifact class able to
            read/write them. The artifact classes distributed with `pond` register automatically
            to the default value, `global_artifact_registry`.
        """
        self.source = source
        self.location = location
        self.datastore = datastore
        self.write_mode = write_mode
        self.author = author
        self.version_name_class = version_name_class
        self.artifact_registry = artifact_registry

        # History of all read versions, will be used as default
        # "inputs" for written tables. Feel free to empty it whenever needed.
        self.read_history: Set[str] = set()
        # Dict[TableRef, List[Version]]: History of all written versions
        self.write_history: Set[str] = set()

    def read_version(self,
                     name: str,
                     version_name: Optional[Union[str, VersionName]] = None,
                     location: Optional[str] = None) -> Version:
        """ Read a version, given its name and version name.

        If no version name is specified, the latest version is read.

        Parameters
        ----------
        name: str
            Artifact name
        version_name: str or VersionName
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.
        location: str, optional
            Location in the data store where artifacts are read. If None, the default location
            specified in the constructor is used.

        Return
        ------
        version: Version
            The loaded Version object.

        See Also
        --------
        `read_artifact` -- Read an Artifact object, including artifact data and metadata
        `read_manifest` -- Read a version manifest, given its name and version name
        `read` -- Read the data in an artifact
        """

        if location is None:
            location = self.location

        versioned_artifact = VersionedArtifact.from_datastore(
            artifact_name=name,
            location=location,
            datastore=self.datastore,
        )
        version = versioned_artifact.read(version_name=version_name)
        version_id = version.get_uri(self.location, self.datastore)
        self.read_history.add(version_id)
        return version

    def read_manifest(self,
                     name: str,
                     version_name: Optional[Union[str, VersionName]] = None,
                     location: Optional[str] = None) -> Manifest:
        """ Read a version manifest, given its name and version name.

        If no version name is specified, the latest version is read.

        Parameters
        ----------
        name: str
            Artifact name
        version_name: str or VersionName
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.
        location: str, optional
            Location in the data store where artifacts are read. If None, the default location
            specified in the constructor is used.

        Return
        ------
        manifest: Manifest
            The loaded Manifest object.

        See Also
        --------
        `read_version` -- Read a Version object, including the artifact object and version manifest
        `read_artifact` -- Read an Artifact object, including artifact data and metadata
        `read` -- Read the data in an artifact
        """

        if location is None:
            location = self.location

        versioned_artifact = VersionedArtifact.from_datastore(
            artifact_name=name,
            location=location,
            datastore=self.datastore,
        )
        manifest = versioned_artifact.read_manifest(version_name)
        return manifest

    def read_artifact(self,
                      name: str,
                      version_name: Optional[Union[str, VersionName]] = None,
                      location: Optional[str] = None) -> Any:
        """ Read an artifact given its name and version name.

        If no version name is specified, the latest version is read.

        Parameters
        ----------
        name: str
            Artifact name
        version_name: str or VersionName
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.
        location: str, optional
            Location in the data store where artifacts are read. If None, the default location
            specified in the constructor is used.

        Return
        ------
        artifact: Artifact
            The loaded artifact

        See Also
        --------
        `read` -- Read the data in an artifact
        `read_manifest` -- Read a version manifest, given its name and version name
        `read_version` -- Read a Version object, including the artifact object and version manifest
        """
        version = self.read_version(name, version_name, location=location)
        return version.artifact

    def read(self,
             name: str,
             version_name: Optional[Union[str, VersionName]] = None,
             location: Optional[str] = None) -> Any:
        """ Read some data given its name and version name.

        If no version name is specified, the latest version is read.

        Parameters
        ----------
        name: str
            Artifact name
        version_name: str or VersionName
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.
        location: str, optional
            Location in the data store where artifacts are read. If None, the default location
            specified in the constructor is used.

        Return
        ------
        data: Any
            The loaded data. The metadata is discarded.

        See Also
        --------
        `read_artifact` -- Read an Artifact object, including artifact data and metadata
        `read_manifest` -- Read a version manifest, given its name and version name
        `read_version` -- Read a Version object, including the artifact object and version manifest
        """

        artifact = self.read_artifact(name, version_name, location=location)
        return artifact.data

    # TODO version name is a string vs is a VersionName instance
    def write(self,
              data: DataType,
              name: str,
              version_name: Optional[Union[str, VersionName]] = None,
              metadata: Optional[Dict[str, str | List]] = None,
              write_mode: Optional[WriteMode] = None,
              location: Optional[str] = None,
              artifact_class: Optional[Type[Artifact]] = None,
              format: Optional[str] = None) -> Version:
        """ Write data as a versioned artifact.

        Parameters
        ----------
        data: DataType
            The artifact data to write.
        name: str
            Name of the artifact.
        format:
        version_name: Union[str, VersionName], optional
            Version name, given as a string (more common) or as VersionName instance. If None,
            the next available version name for the given artifact is used.
        metadata: Dict[str, str | List], optional
            User-defined metadata, saved with the artifact.
            The metadata keys and values are stored as strings.
        write_mode: WriteMode
            Write mode. If None, the global write mode is used (see `Activity.write_mode`). See
            `pond.conventions.WriteMode` for possible values.
        location: str, optional
            Location in the data store where artifacts are written. If None, the default location
            specified in the constructor is used.
        artifact_class: Type[Artifact], optional
            A subclass of `Artifact` to be used to store the data. If None, Activity looks for
            a subclass that knows how to handle the `data` (this is the typical case)
        format: str, optional
            Look for an artifact that can handle this file format.

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

        if artifact_class is None:
            artifact_class = self.artifact_registry.get_artifact(
                data_class=data.__class__,
                format=format,
            )

        if write_mode is None:
            write_mode = self.write_mode

        if location is None:
            location = self.location

        versioned_artifact = VersionedArtifact(
            artifact_name=name,
            location=location,
            datastore=self.datastore,
            artifact_class=artifact_class,
            version_name_class=self.version_name_class,
        )

        manifest = Manifest()
        if metadata is not None:
            user_metadata_source = DictMetadataSource(name='user', metadata=metadata)
            manifest.add_section(user_metadata_source)
        activity_metadata_source = self.get_metadata()
        manifest.add_section(activity_metadata_source)
        version = versioned_artifact.write(
            data=data,
            manifest=manifest,
            version_name=version_name,
            write_mode=write_mode,
        )

        version_uri = version.get_uri(self.location, self.datastore)
        self.write_history.add(version_uri)
        return version

    def get_metadata(self) -> MetadataSource:
        """ Collect activity metadata. """
        activity_metadata = {
            'source': self.source,
            'author': self.author,
            'inputs': sorted(self.read_history),
        }
        return DictMetadataSource(name='activity', metadata=activity_metadata)

    # todo def export() to extract artifact data from a data store
