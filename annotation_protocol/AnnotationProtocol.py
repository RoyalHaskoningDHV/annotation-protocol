import inspect
import logging
from typing import (
    Any,
    Protocol,
    Union,
    _get_protocol_attrs,
    get_args,
    get_origin,
    runtime_checkable,
)

logger = logging.getLogger(__name__)


def _compare_annotations(left: Any, right: Any) -> bool:
    if left in (inspect._empty, Any, None) or right is Any:
        return True
    if get_origin(right) is Union:
        right_types = set(get_args(right))
        if get_origin(left) is Union:
            return set(get_args(left)) <= right_types
        return left in right_types
    return left == right


def _compare_signatures(
    proto_signature: inspect.Signature,
    other_signature: inspect.Signature,
) -> bool:
    # Check return annotations
    if not _compare_annotations(
        proto_signature.return_annotation, other_signature.return_annotation
    ):
        # Other return annotation does not support the return type given in proto
        logger.debug(
            "Return annotation does not support the type given in protocol:"
            f" {proto_signature.return_annotation} vs {other_signature.return_annotation}"
        )
        return NotImplemented

    # Try to match signatures, first make mock parameters from other to bind to proto_signature
    # If proto_signature has a VAR_POSITIONAL param (*args) consider any leftover
    # POSITIONAL_OR_KEYWORD params to be VAR_POSITIONAL
    has_variable_args = any(
        param.kind is inspect.Parameter.VAR_POSITIONAL
        for param in proto_signature.parameters.values()
    )
    other_args = []
    other_kwargs = {}
    for param in other_signature.parameters.values():
        if param.kind is inspect.Parameter.POSITIONAL_ONLY:
            other_args.append(param)
        elif param.kind is inspect.Parameter.KEYWORD_ONLY:
            other_kwargs[param.name] = param
        elif param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if has_variable_args:
                other_args.append(param)
            else:
                other_kwargs[param.name] = param

    # Try to match signatures using the mock parameters
    try:
        bound_params = proto_signature.bind(*other_args, **other_kwargs)
    except TypeError as e:
        # Signature of other does not match signature of proto
        logger.debug(f"Params are different: {e}")
        return NotImplemented

    # Check annotations of all non-args/kwargs parameters
    for proto_param, other_param in (
        (param, bound_params.arguments[param.name])
        for param in proto_signature.parameters.values()
        if param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ):
        if (
            proto_param.kind is not inspect.Parameter.POSITIONAL_ONLY
            and proto_param.name != other_param.name
        ):
            # Name of potential keyword argument is different in other
            logger.debug(
                "Name of potential keyword argument is different:"
                f" {proto_param.name} != {other_param.name}"
            )
            return NotImplemented

        if (
            proto_param.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
            and other_param.kind is inspect.Parameter.POSITIONAL_ONLY
        ):
            # potential keyword argument can only be positional in other
            logger.debug(f"Potential keyword argument {proto_param.name} is positional-only")
            return NotImplemented

        if not _compare_annotations(proto_param.annotation, other_param.annotation):
            # Other annotation does not support the type given in proto
            logger.debug(
                f"Annotation for {proto_param.name} does not support the type given in protocol:"
                " {proto_param.annotation} vs {other_param.annotation}"
            )
            return NotImplemented
    return True


def _check_annotations(proto, other):
    for attr in _get_protocol_attrs(proto):
        # Skip any attrs from AnnotationProtocol itself (I.e. __init_subclasses__)
        if hasattr(AnnotationProtocol, attr):
            continue

        # Skip if attr doesn't have annotations in the protocol
        try:
            proto_attr = getattr(proto, attr, None)
            proto_signature = inspect.signature(proto_attr)
        except TypeError:
            continue

        for base in other.__mro__:
            if not hasattr(base, attr):
                continue
            try:
                other_attr = getattr(base, attr)
                other_signature = inspect.signature(other_attr)
            except TypeError:
                # attr is not a callable in other
                logger.debug(f"{attr} is not a callable in {other} base {base}")
                return NotImplemented

            logger.debug(f"Comparing signature of {attr} in {other} base {base}")
            compare = _compare_signatures(proto_signature, other_signature)
            if compare is not True:
                return compare
            break
        else:
            # This means attr is not in any class of other's MRO
            return NotImplemented
    return True


class _AnnotationProtocolMeta(type(Protocol)):
    def __instancecheck__(cls: Any, instance: Any) -> bool:
        if getattr(cls, "_is_protocol", False):
            for attr in _get_protocol_attrs(cls):
                if (
                    not hasattr(AnnotationProtocol, attr)
                    and not callable(getattr(cls, attr, None))
                    and not hasattr(instance, attr)
                ):
                    # Missing data attributes
                    logger.debug(f"Missing data attributes: {attr}")
                    return super(type(Protocol), cls).__instancecheck__(instance)
            # instance may actually be a proper class rather than an instance
            check = _check_annotations(
                cls, instance if isinstance(instance, type) else instance.__class__
            )
            if isinstance(check, bool):
                return check
        return super(type(Protocol), cls).__instancecheck__(instance)


class AnnotationProtocol(Protocol, metaclass=_AnnotationProtocolMeta):
    def __init_subclass__(cls) -> None:
        cls._is_protocol = any(b is AnnotationProtocol for b in cls.__bases__)  # type: ignore
        runtime_checkable(cls)
        super().__init_subclass__()

        # Save the usual __subclasshook__ from Protocol to check first
        ignore_annotations_subclasshook = cls.__subclasshook__

        def _annotation_strict_subclasshook(other: Any) -> bool:
            # No need to check annotations if it doesn't pass the Protocol check already
            ignore_annotations_check = ignore_annotations_subclasshook(other)
            if ignore_annotations_check is not True:
                return ignore_annotations_check
            return _check_annotations(cls, other)

        cls.__subclasshook__ = _annotation_strict_subclasshook  # type: ignore
