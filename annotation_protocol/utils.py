import logging
from collections.abc import Generator
from inspect import Parameter, Signature, _empty, signature
from types import UnionType
from typing import (
    Any,
    Union,
    _get_protocol_attrs,
    get_args,
    get_origin,
)

logger = logging.getLogger(__name__)


UNION_TYPES = (Union, UnionType)


def attributes_to_check(
    protocol: object,
    ignore_attributes: set[str],
) -> Generator[tuple[object, Signature], None, None]:
    """Generate attributes (and their signature) of protocol that need to be checked.

    It only retrieves attributes that have an annotation.

    Attributes
    ----------
        protocol (object): the protocol to get attributes from.
        ignore_attributes (set[str]): the annotation protocol class specific methods.

    Yields
    ------
        Generator[tuple[object, Signature], None, None]: _description_
    """
    protocol_attributes: set[int] = _get_protocol_attrs(protocol)
    for attr in protocol_attributes.difference(ignore_attributes):
        try:
            protocol_attr = getattr(protocol, attr, None)
            protocol_signature = signature(protocol_attr, eval_str=True)
        except TypeError:
            msg = f"{attr} doesn't have annotations in the protocol."
            logger.debug(msg)
            continue
        else:
            yield attr, protocol_signature


def mock_parameters(
    protocol: Signature,
    other: Signature,
) -> tuple[list[Parameter], dict[str, Parameter]]:
    """Make mock parameters from other to bind to protocol.

    If proto has a VAR_POSITIONAL param (*args) consider any
    leftover POSITIONAL_OR_KEYWORD params to be VAR_POSITIONAL.

    Attributes
    ----------
        protocol (Signature): _description_
        other (Signature): _description_

    Returns
    -------
        list[Parameter]: other_args
        dict[str, Parameter]: other_kwargs
    """
    has_variable_args = any(
        param.kind is Parameter.VAR_POSITIONAL for param in protocol.parameters.values()
    )
    other_args, other_kwargs = [], {}
    for param in other.parameters.values():
        match param.kind:
            case Parameter.POSITIONAL_ONLY:
                other_args.append(param)
            case Parameter.KEYWORD_ONLY:
                other_kwargs[param.name] = param
            case Parameter.POSITIONAL_OR_KEYWORD if has_variable_args:
                other_args.append(param)
            case Parameter.POSITIONAL_OR_KEYWORD if not has_variable_args:
                other_kwargs[param.name] = param
    return other_args, other_kwargs


def get_signature(obj: object, attr: object) -> Signature | None:
    """Get the signature of an attribute in an object.

    This searches superclasses of the object using the Method Resolution Order.

    Attributes
    ----------
        obj (object): the object to search in.
        attr (object): the attribute to find.

    Returns
    -------
        Signature | None: returns the signature or None if not found.
    """
    for base in [b for b in obj.__mro__ if hasattr(b, attr)]:
        try:
            obj_attr = getattr(base, attr)
            return signature(obj_attr, eval_str=True)
        except TypeError:
            msg = f"{attr} is not a callable in {obj} with MRO {base=}."
            logger.debug(msg)
            return None
    return None


def compare_annotations(protocol: object, other: object) -> bool:
    """Compare 2 annotations of protocol and class `other` that should adhere to it.

    Attributes
    ----------
        protocol (object): The `protocol` that `other` should adhere to
        other (object): The class `other` that should adhere to the `protocol`

    Returns
    -------
        bool: True when annotations of class `other` are also in `protocol`
    """
    if protocol in (_empty, Any, None) or other is Any:
        return True

    if get_origin(protocol) in UNION_TYPES:
        protocol_types = set(get_args(protocol))
        other_types = set(get_args(other)) if get_origin(other) in UNION_TYPES else {other}
        return protocol_types >= other_types
    return protocol == other


def return_annotations_equal(protocol: object, other: object) -> bool:
    """Compare return annotations of two signatures.

    Attributes
    ----------
        protocol (object): The `protocol` that `other` should adhere to
        other (object): The class `other` that should adhere to the `protocol`

    Returns
    -------
        bool: True if the two return annotations are equal
    """
    if not compare_annotations(protocol.return_annotation, other.return_annotation):
        msg = (
            "Return annotation does not support the type given in protocol:",
            f" {protocol.return_annotation} vs {other.return_annotation}",
        )
        logger.debug(msg)
        return False
    return True


def argument_annotations_equal(protocol: object, other: object) -> bool:
    """Compare all argument annotations of two signatures.

    Attributes
    ----------
        protocol (object): The `protocol` that `other` should adhere to
        other (object): The class `other` that should adhere to the `protocol`

    Returns
    -------
        bool: True if the two argument annotations are equal
    """
    # check annotations of all args and kwargs parameters
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
