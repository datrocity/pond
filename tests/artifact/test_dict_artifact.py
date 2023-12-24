import pytest

from pond.artifact.dict_artifact import DictArtifact


@pytest.fixture
def dict_():
    data = {
        'a': [1, 2, 3],
        'b': 17.2,
        'c': {'x': 'abc'}
    }
    return data


@pytest.fixture
def metadata():
    metadata = {
        'source': 'test_to_csv_stream a b',
        'm1': 12.3,
    }
    return metadata


def test_filename(tmp_path, dict_):
    artifact = DictArtifact(dict_)
    assert artifact.filename('a/b') == 'a/b.json'


def test_write_bytes(tmp_path, dict_, metadata):
    expected = (
        '{"a": [1, 2, 3], '
        '"b": 17.2, '
        '"c": {"x": "abc"}, '
        '"__metadata__": {"source": "test_to_csv_stream a b", "m1": "12.3"}}'
        .strip()
        .replace('\n', ' ')
    )

    artifact = DictArtifact(dict_, metadata)
    with open(tmp_path / 'test.csv', 'wb') as f:
        artifact.write_bytes(f)

    with open(tmp_path / 'test.csv', 'rb') as f:
        content = f.read().decode()
    assert content == expected


def test_read_bytes(tmp_path, dict_, metadata):
    original = DictArtifact(dict_, metadata)
    original.write(tmp_path / 'test.csv')

    with open(tmp_path / 'test.csv', 'rb') as f:
        artifact = DictArtifact.read_bytes(f)

    assert artifact.data == dict_
    assert artifact.metadata == {k: str(v) for k, v in original.metadata.items()}
