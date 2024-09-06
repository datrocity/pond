from matplotlib.pyplot import Figure
import numpy as np
import pandas as pd
from PIL import Image


def test_register_on_package_import():
    # We expect the basic artifacts to be registered in the global artifact registry when the
    # `pond.artifact` package is first imported

    import pond.artifact
    from pond.artifact.artifact_registry import global_artifact_registry

    expected_classes = [
        pd.DataFrame,
        Figure,
        Image,
        np.array,
        dict,
    ]
    for class_ in expected_classes:
        artifact_classes = global_artifact_registry.get_available_artifacts(class_)
        assert len(artifact_classes) > 0, f"{class_} not registered"
