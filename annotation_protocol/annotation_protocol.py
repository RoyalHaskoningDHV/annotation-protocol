import logging
from typing import (
    Protocol,
    _get_protocol_attrs,
    runtime_checkable,
)

from typing_extensions import Self

from .check_annotations import check_annotations

logger = logging.getLogger(__name__)


class _AnnotationProtocolMeta(type(Protocol)):
    def __instancecheck__(cls: Self, instance: object) -> bool:
        if getattr(cls, "_is_protocol", False):
            for attr in _get_protocol_attrs(cls):
                if (
                    not hasattr(AnnotationProtocol, attr)
                    and not callable(getattr(cls, attr, None))
                    and not hasattr(instance, attr)
                ):
                    msg = f"Missing data attributes: {attr}."
                    logger.debug(msg)
                    return super().__instancecheck__(instance)
            # instance may actually be a proper class rather than an instance
            check = check_annotations(
                cls,
                instance if isinstance(instance, type) else instance.__class__,
                AnnotationProtocol,
            )
            if isinstance(check, bool):
                return check
        return super(type(Protocol), cls).__instancecheck__(instance)


class AnnotationProtocol(Protocol, metaclass=_AnnotationProtocolMeta):
    def __init_subclass__(cls: Self) -> None:
        cls._is_protocol = any(  # type: ignore[attr-defined]
            b is AnnotationProtocol for b in cls.__bases__
        )
        runtime_checkable(cls)
        super().__init_subclass__()

        # Save the usual __subclasshook__ from Protocol to check first
        ignore_annotations_subclasshook = cls.__subclasshook__

        def _annotation_strict_subclasshook(other: object) -> bool:
            # No need to check annotations if it doesn't pass the Protocol check already
            ignore_annotations_check = ignore_annotations_subclasshook(other)
            if ignore_annotations_check is not True:
                return ignore_annotations_check
            return check_annotations(cls, other, AnnotationProtocol)

        cls.__subclasshook__ = _annotation_strict_subclasshook  # type: ignore[attr-defined]
