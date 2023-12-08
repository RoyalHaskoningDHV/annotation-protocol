import logging
from collections.abc import Generator
from inspect import Parameter, Signature, signature
from typing import _get_protocol_attrs

logger = logging.getLogger(__name__)


def attributes_to_check(
    protocol: object,
    ignore_attributes: set[str],
) -> Generator[tuple[object, Signature], None, None]:
    """Generate attributes (and their signature) of protocol that need to be checked.

    It only retrieves attributes that have an annotation.

    Attributes
    ----------
        protocol (object): the protocol to get attributes from.
        ignore_attributes (set[str]): the annotastion protocol class.

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
