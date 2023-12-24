from typing import Any, Dict, Optional, Set, Type, Union

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
                 author: str='NA',
                 version_name_class: Type[VersionName] = SimpleVersionName,
                 artifact_registry: ArtifactRegistry = global_artifact_registry):
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
        author: str
            Author name/identifier, used as metadata. Default is 'NA'.
        version_name_class: VersionName
            Class used to create increasing version names. The default value,
            `SimpleVersionName` creates version names as `v1`, `v2`, etc.
        artifact_registry: ArtifactRegistry
            Registry object mapping data types and file formats to an artifact class able to
            read/write them. The artifact classes distributed with `pond` register automatically
            to the default value,  `global_artifact_registry`.
        """
        self.source = source
        self.location = location
        self.datastore = datastore
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
                     version_name: Optional[Union[str, VersionName]] = None) -> Version:
        """ Read a version, given its name and version name.

        If no version name is specified, the latest version is read.

        Parameters
        ----------
        name: str
            Artifact name
        version_name: str or VersionName
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.

        Return
        ------
        version: Version
            The loaded Version object.

        See Also
        --------
        `read_artifact` -- Read an Artifact object, including artifact data and metadata
        `read` -- Read the data in an artifact
        """
        versioned_artifact = VersionedArtifact.from_datastore(
            artifact_name=name,
            location=self.location,
            datastore=self.datastore,
        )
        version = versioned_artifact.read(version_name=version_name)
        version_id = version.get_uri(self.location, self.datastore)
        self.read_history.add(version_id)
        return version

    def read_artifact(self,
                      name: str,
                      version_name: Optional[Union[str, VersionName]] = None) -> Any:
        """ Read an artifact given its name and version name.

        If no version name is specified, the latest version is read.

        Parameters
        ----------
        name: str
            Artifact name
        version_name: str or VersionName
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.

        Return
        ------
        artifact: Artifact
            The loaded artifact

        See Also
        --------
        `read` -- Read the data in an artifact
        `read_version` -- Read a Version object, including the artifact object and version manifest
        """
        version = self.read_version(name, version_name)
        return version.artifact

    def read(self,
             name: str,
             version_name: Optional[Union[str, VersionName]] = None) -> Any:
        """ Read some data given its name and version name.

        If no version name is specified, the latest version is read.

        Parameters
        ----------
        name: str
            Artifact name
        version_name: str or VersionName
            Version name, given as a string (more common) or as VersionName instance. If None,
            the latest version name for the given artifact is used.

        Return
        ------
        data: Any
            The loaded data. The metadata is discarded.

        See Also
        --------
        `read_artifact` -- Read an Artifact object, including artifact data and metadata
        `read_version` -- Read a Version object, including the artifact object and version manifest
        """
        artifact = self.read_artifact(name, version_name)
        return artifact.data

    # TODO version name is a string vs is a VersionName instance
    def write(self,
              data: DataType,
              name: str,
              artifact_class: Optional[Type[Artifact]] = None,
              format: Optional[str] = None,
              version_name: Optional[Union[str, VersionName]] = None,
              metadata: Optional[Dict[str, str]] = None,
              write_mode: WriteMode = WriteMode.ERROR_IF_EXISTS) -> Version:
        # todo: write mode

        if artifact_class is None:
            artifact_class = self.artifact_registry.get_artifact(
                data_class=data.__class__,
                format=format,
            )

        versioned_artifact = VersionedArtifact(
            artifact_name=name,
            location=self.location,
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
