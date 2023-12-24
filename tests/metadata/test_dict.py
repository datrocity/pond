from pond.metadata.dict import DictMetadataSource


def test_dict_metadata_source():
    metadata = {'a': 123, 'foo': [1, 2, 3]}
    source = DictMetadataSource(name='foo', metadata=metadata)

    assert source.section_name() == 'foo'
    expected = {'a': '123', 'foo': '[1, 2, 3]'}
    assert source.collect() == expected
