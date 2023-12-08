import logging
from inspect import Signature

from .utils import (
    argument_annotations_equal,
    attributes_to_check,
    get_signature,
    return_annotations_equal,
)

logger = logging.getLogger(__name__)


def compare_signatures(
    protocol: Signature,
    other: Signature,
) -> bool:
    """Compare 2 signatures and return if they are equal.

    This includes return annotations,annotations of args and kwargs, and

    Attributes
    ----------
        protocol (object): The `protocol` that `other` should adhere to
        other (object): The class `other` that should adhere to the `protocol`

    Returns
    -------
        bool: True when signatures of class `other` are equal to `protocol`
    """
    return return_annotations_equal(protocol, other) and argument_annotations_equal(
        protocol,
        other,
    )


def check_annotations(
    protocol: object,
    other: object,
    ignore_attributes: set[str],
) -> bool | type[NotImplemented]:
    """Check whether the annotations of an object comply to the protocol.

    Attributes
    ----------
        protocol (object): The `protocol` that `other` should adhere to
        other (object): The class `other` that should adhere to the `protocol`
        ignore_attributes (set[str]): Do not compare these attributes

    Returns
    -------
        bool | type[NotImplemented]: Outcome of the comparison
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
