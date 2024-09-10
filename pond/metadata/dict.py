from typing import Any

from pond.metadata.metadata_source import MetadataSource, transform_metadata_value


class DictMetadataSource(MetadataSource):

    def __init__(self, name: str, metadata: dict[str, Any]):
        """ A dictionary used as source of metadata.

        Parameters
        ----------
        name: str
            The name of the section represented by this metadata source.
        metadata: dict[str, Any]
            The dictionary of metadata. Values will be converted to string (or a list of strings
            if the value is a list).
        """
        self.name = name
        self.metadata = metadata

    def section_name(self) -> str:
        return self.name

    def collect(self) -> dict[str, str]:
        return {k: transform_metadata_value(v) for k,v in self.metadata.items()}
