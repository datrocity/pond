from abc import abstractmethod


def transform_metadata_value(value):
    """ Make sure that each value is either a list or a string. """
    if isinstance(value, list):
        transformed = [transform_metadata_value(el) for el in value]
    else:
        transformed = str(value)
    return transformed


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
