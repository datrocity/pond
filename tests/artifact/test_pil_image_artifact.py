import matplotlib.pyplot as plt
import numpy as np
from PIL.Image import Image
import pytest

from pond.artifact.pil_image_artifact import PILImageArtifact


@pytest.fixture
def fig():
    x = np.linspace(0, 1, 100)
    y = np.sin(2*np.pi*x)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    return fig


@pytest.fixture
def metadata():
    metadata = {
        'source': 'test_to_csv_stream a b',
        'm1': 12.3,
    }
    return metadata


def test_from_matplotlib_fig(fig, metadata):
    artifact = PILImageArtifact.from_matplotlib_fig(fig, metadata)

    assert artifact.metadata == metadata
    assert isinstance(artifact.data, Image)


def test_write_read_bytes(tmp_path, fig, metadata):
    original = PILImageArtifact.from_matplotlib_fig(fig, metadata)

    with open(tmp_path / 'test.png', 'wb') as f:
        original.write_bytes(f)

    with open(tmp_path / 'test.png', 'rb') as f:
        reloaded = original.read_bytes(f)

    assert reloaded.metadata == {k: str(v) for k, v in metadata.items()}
    assert isinstance(reloaded.data, Image)
    assert reloaded.data.size == fig.canvas.get_width_height()
