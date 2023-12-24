import pytest

from pond.artifact import Artifact
from pond.artifact.artifact_registry import ArtifactRegistry
from pond.exceptions import FormatNotFound, ArtifactNotFound


class MockArtifactCSV(Artifact):
    pass


class MockArtifactExcel(Artifact):
    pass


@pytest.fixture()
def registry():
    registry = ArtifactRegistry()
    registry.register(MockArtifactCSV, list, format='csv')
    registry.register(MockArtifactExcel, list, format='xlsx')
    return registry


def test_lookup_with_format(registry):
    # look-up with format
    cls = registry.get_artifact(list, format='csv')
    assert cls == MockArtifactCSV


def test_lookup_no_format(registry):
    # look-up without format, return last inserted
    cls = registry.get_artifact(list)
    assert cls == MockArtifactExcel


def test_lookup_format_not_found(registry):
    # look-up, format is not registry
    with pytest.raises(FormatNotFound) as excinfo:
        registry.get_artifact(list, format='foo')

    msg = str(excinfo.value)
    assert 'foo' in msg
    assert 'list' in msg


def test_lookup_data_type_not_found(registry):
    # look-up, format is not registry
    with pytest.raises(ArtifactNotFound) as excinfo:
        registry.get_artifact(dict, format='foo')

    msg = str(excinfo.value)
    assert 'dict' in msg


def test_get_available_artifacts(registry):
    artifact_classes = registry.get_available_artifacts(list)

    expected = [(MockArtifactCSV, 'csv'), (MockArtifactExcel, 'xlsx')]
    assert artifact_classes == expected
