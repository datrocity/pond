from collections import defaultdict, namedtuple

from pond.exceptions import ArtifactNotFound, FormatNotFound


ArtifactRegistryItem = namedtuple('ArtifactRegistryItem', ['artifact_class', 'format'])


# todo: handle subclasses of a data class

class ArtifactRegistry:
    """ Registry of data types to compatible artifact classes. """

    def __init__(self):
        self._register = defaultdict(list)

    def register(self, artifact_class, data_class, format=None):
        item = ArtifactRegistryItem(artifact_class=artifact_class, format=format)
        self._register[data_class].append(item)

    def get_available_artifacts(self, data_class):
        """ Get all available artifacts for a given data class.

        Parameters
        ----------
        data_class: class
            Data class for which we need to find an adapter.

        Returns
        -------
        items: list of ArtifactRegistryItem
            All registered (artifact, format) items compatible with data_class.
        """
        return self._register[data_class]

    def get_artifact(self, data_class, format=None):
        """
        In case multiple artifacts are available for the same data class and format,
        the last registered artifact is returned.

        Parameters
        ----------
        data_class: class
            Data class for which we need to find an adapter.
        format: str
            We require an adapter that can handle this file format.

        Returns
        -------
        artifact_class: class
            Artifact class

        """
        items = self.get_available_artifacts(data_class)
        if len(items) == 0:
            raise ArtifactNotFound(data_class)

        if format is None:
            artifact_class = items[-1].artifact_class
        else:
            for item in items:
                if item.format == format:
                    artifact_class = item.artifact_class
                    break
            else:
                raise FormatNotFound(data_class, format)

        return artifact_class


global_artifact_registry = ArtifactRegistry()
