from pond.metadata.dict import DictMetadataSource


class Manifest:

    # --- Manifest class interface

    def __init__(self):
        self._sections = {}

    @classmethod
    def from_yaml(cls, manifest_location, datastore):
        """

        Parameters
        ----------
        manifest_location
        datastore

        Returns
        -------

        """
        manifest_dict = datastore.read_yaml(manifest_location)
        return cls.from_nested_dict(manifest_dict)

    @classmethod
    def from_nested_dict(cls, manifest_dict: dict):
        manifest = cls()
        for section_name, metadata in manifest_dict.items():
            # TODO make this a FrozendictMetadataSource
            source = DictMetadataSource(name=section_name, metadata=metadata)
            manifest.add_section(source)
        return manifest

    # --- Manifest public interface

    def to_yaml(self, manifest_location, datastore):
        metadata = self.collect()
        datastore.write_yaml(manifest_location, metadata)

    def add_section(self, metadata_source):
        """

        Parameters
        ----------
        metadata_source
            If None, nothing is added but no exception is raised.

        Returns
        -------

        """
        if metadata_source is not None:
            self._sections[metadata_source.section_name()] = metadata_source

    def collect_section(self, name, default_metadata=None):
        source = self._sections.get(name, None)
        if source is None:
            metadata = default_metadata
        else:
            metadata = source.collect()
        return metadata

    def collect(self):
        dict_ = {}
        for name, source in self._sections.items():
            source_metadata = {k: str(v) for k, v in source.collect().items()}
            dict_[name] = source_metadata
        return dict_
