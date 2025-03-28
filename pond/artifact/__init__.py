from pond.artifact.artifact import Artifact
from pond.artifact.artifact_registry import global_artifact_registry
# Importing the artifacts also has the side effect of registering them
from pond.artifact.dict_artifact import DictArtifact
from pond.artifact.numpy_array_artifact import NumpyArrayArtifact, NumpyArrayCompressedArtifact
from pond.artifact.pandas_dataframe_artifact import PandasDataFrameArtifact
from pond.artifact.pil_image_artifact import PILImageArtifact
