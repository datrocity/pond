from enum import Enum, unique
from typing import TypeVar

from pond.version_name import VersionName


DataType = TypeVar('DataType')


@unique
class WriteMode(str, Enum):
    """Version write save modes"""

    #: If a version already exists, it is first deleted and then written
    OVERWRITE = 'overwrite'
    #: If a version already exists, an error is raised (this is generally the default behavior)
    ERROR_IF_EXISTS = 'errorifexists'


MANIFEST_FILENAME = 'manifest.yml'
METADATA_DIRNAME = '_pond'
TXT_ENCODING = 'utf-8'
VERSIONS_LOCK_FILENAME = '_VERSIONS_LOCK'


def urijoinpath(*parts: str) -> str:
    """Joins two uri path components, also ensure the right part does not end with a slash"""
    # TODO: use os.path.join
    return '/'.join([part.rstrip('/') for part in parts])


def versioned_artifact_location(location: str, artifact_name: str):
    return urijoinpath(location, artifact_name)


def version_location(location: str, version_name: VersionName) -> str:
    return urijoinpath(location, str(version_name))


def versions_lock_file_location(location: str) -> str:
    return urijoinpath(location, METADATA_DIRNAME, VERSIONS_LOCK_FILENAME)


def version_data_location(version_location: str, data_filename: str) -> str:
    return urijoinpath(version_location, data_filename)


#todo: use or remove
def version_manifest_location(version_location: str) -> str:
    """ Manifest location with respect to a version root. """
    return urijoinpath(version_location, METADATA_DIRNAME, MANIFEST_FILENAME)


def version_uri(datastore_id: str, location: str, artifact_name: str, version_name: VersionName):
    uri = f'pond://{datastore_id}/{location}/{artifact_name}/{str(version_name)}'
    return uri
