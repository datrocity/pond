import matplotlib.pyplot as plt
import numpy as np
from PIL.Image import Image
import pytest

from pond.activity import Activity
from pond.artifact.pil_image_artifact import PILImageArtifact, _image_from_matplotlib_fig
from pond.storage.file_datastore import FileDatastore


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


def test_from_matplotlib_fig(fig):
    data = _image_from_matplotlib_fig(fig)
    assert isinstance(data, Image)


def test_write_read_bytes(tmp_path, fig, metadata):
    data = _image_from_matplotlib_fig(fig)
    original = PILImageArtifact(data, metadata=metadata)

    with open(tmp_path / 'test.png', 'wb') as f:
        original.write_bytes(f)

    with open(tmp_path / 'test.png', 'rb') as f:
        reloaded = original.read_bytes(f)

    assert reloaded.metadata == {k: str(v) for k, v in metadata.items()}
    assert isinstance(reloaded.data, Image)
    assert reloaded.data.size == fig.canvas.get_width_height()


def test_write_read_matplotlib_figure(tmp_path, fig):
    activity = Activity(
        source='test_pond.py',
        datastore=FileDatastore(id='foostore', base_path=tmp_path),
        location='test_location',
    )

    activity.write(fig, 'matplotlib_figure')
    artifact = activity.read_artifact('matplotlib_figure')
    assert isinstance(artifact, PILImageArtifact)
