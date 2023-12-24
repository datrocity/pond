from typing import Type


class IncompatibleVersionName(Exception):

    def __init__(self, version_name: 'VersionName', version_name_class: Type['VersionName']):
        msg = (f'Version name: "{version_name}" not of type "{version_name_class.__name__}".')
        super().__init__(msg)


class InvalidVersionName(Exception):

    def __init__(self, version_name: str):
        super().__init__(f'Invalid version name: {version_name}.')


class VersionDoesNotExist(Exception):

    def __init__(self, artifact_location: str, version_name: str):
        super().__init__(f'Version "{version_name}" does not exist at "{artifact_location}".')


class VersionAlreadyExists(Exception):

    def __init__(self, version_uri: str):
        super().__init__(f'Version already exists:  {version_uri}.')


class ArtifactVersionsIsLocked(Exception):

    def __init__(self, artifact_location: str):
        super().__init__(
            f'Cannot create the new artifact version "{artifact_location}" because it is locked.')


class FormatNotFound(Exception):
    def __init__(self, data_class, format):
        super().__init__(
            f"Artifact with format '{format}' compatible with data type '{data_class.__name__}' not found."
        )


class ArtifactNotFound(Exception):
    def __init__(self, data_class):
        super().__init__(
            f"No artifact compatible with data type '{data_class.__name__}'."
        )
