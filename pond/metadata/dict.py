from typing import Any

from pond.metadata.metadata_source import MetadataSource


class DictMetadataSource(MetadataSource):

    def __init__(self, name: str, metadata: dict[str, Any]):
        """ A dictionary used as source of metadata.

        Parameters
        ----------
        name: str
            The name of the section represented by this metadata source.
        metadata: dict[str, Any]
            The dictionary of metadata. Values will be converted to string.
        """
        self.name = name
        self.metadata = metadata

    def section_name(self) -> str:
        return self.name

    def collect(self) -> dict[str, str]:
        return {k: str(v) for k,v in self.metadata.items()}
