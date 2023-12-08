import logging
from inspect import Parameter, Signature, _empty
from types import UnionType
from typing import (
    Any,
    Union,
    get_args,
    get_origin,
)

from .utils import attributes_to_check, get_signature, mock_parameters

logger = logging.getLogger(__name__)

UNION_TYPES = (Union, UnionType)


def compare_annotations(protocol: object, other: object) -> bool:
    """Compare 2 annotations and return if they are equal.

    Attributes
    ----------
        protocol (object): _description_
        other (object): _description_

    Returns
    -------
        bool: _description_
    """
    if protocol in (_empty, Any, None) or other is Any:
        return True

    if get_origin(protocol) in UNION_TYPES:
        protocol_types = set(get_args(protocol))
        other_types = set(get_args(other)) if get_origin(other) in UNION_TYPES else {other}
        return protocol_types >= other_types
    return protocol == other


def compare_signatures(
    protocol: Signature,
    other: Signature,
) -> bool:
    """Compare 2 signatures and return if they are equal.

    Attributes
    ----------
        left (object): _description_
        right (object): _description_

    Returns
    -------
        bool: _description_
    """
    # Try to match return signatures.
    if not compare_annotations(protocol.return_annotation, other.return_annotation):
        msg = (
            "Return annotation does not support the type given in protocol:",
            f" {protocol.return_annotation} vs {other.return_annotation}",
        )
        logger.debug(msg)
        return False

    # Try to match signatures using the mock parameters.
    other_args, other_kwargs = mock_parameters(protocol, other)
    try:
        bound_params = protocol.bind(*other_args, **other_kwargs)
    except TypeError as e:
        msg = f"Signature of other does not match signature of protocol: {e}"
        logger.debug(msg)
        return False

    # Check annotations of all non-args/kwargs parameters.
    non_arg_kwarg_params = filter(
        lambda p: p.kind not in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD),
        protocol.parameters.values(),
    )
    for protocol_param in non_arg_kwarg_params:
        other_param = bound_params.arguments[protocol_param.name]
        if (
            protocol_param.kind is not Parameter.POSITIONAL_ONLY
            and protocol_param.name != other_param.name
        ):
            msg = (
                "Name of potential keyword argument is different:",
                f" {protocol_param.name} != {other_param.name}",
            )
            logger.debug(msg)
            return False

        if (
            protocol_param.kind is Parameter.POSITIONAL_OR_KEYWORD
            and other_param.kind is Parameter.POSITIONAL_ONLY
        ):
            msg = f"Potential keyword argument {protocol_param.name} is positional-only"
            logger.debug(msg)
            return False

        if not compare_annotations(protocol_param.annotation, other_param.annotation):
            msg = (
                f"Annotation for {protocol_param.name} does not ",
                "support the type given in protocol: ",
                f"{protocol_param.annotation} vs {other_param.annotation}",
            )
            logger.debug(msg)
            return False
    return True


def check_annotations(
    protocol: object,
    other: object,
    ignore_attributes: set[str],
) -> bool | type[NotImplemented]:
    """Check whether the annotations of an object comply to the protocol.

    Attributes
    ----------
        protocol (object): _description_
        other (object): _description_
        ignore_attributes (set[str]): _description_

    Returns
    -------
        bool | type[NotImplemented]: _description_
    """
    for attr, protocol_signature in attributes_to_check(protocol, ignore_attributes):
        if not (other_signature := get_signature(other, attr)):
            msg = f"`{attr}` is not in any class of {other}'s MRO."
            logger.debug(msg)
            return NotImplemented

        msg = f"Comparing signature of `{attr}` in {other} against protocol."
        logger.debug(msg)
        if not (compare := compare_signatures(protocol_signature, other_signature)):
            return compare
    return True
