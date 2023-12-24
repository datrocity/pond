from abc import abstractmethod


class MetadataSource:
    """ Represents a source of metadata.

    The metadata is collected using the `collect` method. Note that two calls to `collect` can
    return different values, as the metadata could be collected on the fly, as in the case of a
    time stamp, a git SHA, or other.

    Metadata keys and values must both be strings.
    """

    @abstractmethod
    def section_name(self) -> str:
        """ Name of the section in the manifest corresponding to this metadata. """
        return ''

    @abstractmethod
    def collect(self) -> dict[str, str]:
        """ Collect all the metadata in a dictionary.

        Keys and values must both be strings.
        """
        return {}
