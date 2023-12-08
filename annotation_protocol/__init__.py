"""Protocol that checks attribute and function annotations.

The AnnotationProtocol class extends the `isinstance` check of python to be more strict
and assess the following in addition to whether the `object` is an instance of the
`classinfo` argument.
"""
from .annotation_protocol import AnnotationProtocol
from .check_annotations import check_annotations

__all__ = [
    "AnnotationProtocol",
    "check_annotations",
]
