import unittest
from collections.abc import Callable
from typing import Any

from annotation_protocol import AnnotationProtocol


class TestAnnotationProtocol(unittest.TestCase):
    def test_missing_callable_attr(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(x):
                ...

        class Missing:
            pass

        assert not isinstance(Missing(), Proto)

    def test_missing_data_attr(self):
        class Proto(AnnotationProtocol):
            data: int

        class OnlyAfterInit:
            def __init__(self) -> None:
                self.data = 123

        assert not isinstance(OnlyAfterInit, Proto)
        assert isinstance(OnlyAfterInit(), Proto)

    def test_not_a_callable(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(x: int):
                ...

        class NotACallable:
            f: int

        assert not isinstance(NotACallable(), Proto)

    def test_missing_params(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, *, key_only: int):
                ...

        class MissingPosOnly:
            @staticmethod
            def f(pos_or_key: int, *, key_only: int):
                ...

        class MissingPosOrKey:
            @staticmethod
            def f(pos_only: int, /, *, key_only: int):
                ...

        class MissingKeyOnly:
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int):
                ...

        assert not isinstance(MissingPosOnly(), Proto)
        assert not isinstance(MissingPosOrKey(), Proto)
        assert not isinstance(MissingKeyOnly(), Proto)

    def test_bound_methods(self):
        class Proto(AnnotationProtocol):
            def instancemeth(self):
                ...

            @classmethod
            def classmeth(cls):
                ...

        class Test:
            def instancemeth(self):
                ...

            @classmethod
            def classmeth(cls):
                ...

        class NoClassMethod:
            def instancemeth(self):
                ...

            def classmeth(cls):
                ...

        assert isinstance(Test(), Proto)
        assert not isinstance(NoClassMethod(), Proto)

    def test_no_params(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f():
                ...

        class NoParams:
            @staticmethod
            def f():
                ...

        class ExtraParams:
            @staticmethod
            def f(x):
                ...

        class VarPos:
            @staticmethod
            def f(*args):
                ...

        class VarKey:
            @staticmethod
            def f(**kwargs):
                ...

        class BoundMethod:
            def f(self):
                ...

        assert isinstance(NoParams(), Proto)
        assert not isinstance(ExtraParams(), Proto)
        assert isinstance(VarPos(), Proto)
        assert isinstance(VarKey(), Proto)
        assert not isinstance(BoundMethod(), Proto)

    def test_extra_params(self):
        class NoVarProto(AnnotationProtocol):
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, *, key_only: int):
                ...

        class VarPosProto(AnnotationProtocol):
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, *args, key_only: int):
                ...

        class VarKeyProto(AnnotationProtocol):
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, *, key_only: int, **kwargs):
                ...

        class VarBothProto(AnnotationProtocol):
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, *args, key_only: int, **kwargs):
                ...

        class ExtraPosOnly:
            @staticmethod
            def f(pos_only: int, extra_pos_only: int, /, pos_or_key: int, *, key_only: int):
                ...

        class ExtraPosOrKey:
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, extra_pos_or_key: int, *, key_only: int):
                ...

        class ExtraKeyOnly:
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, *, key_only: int, extra_key_only: int):
                ...

        assert not isinstance(ExtraPosOnly(), NoVarProto)
        assert not isinstance(ExtraPosOnly(), VarPosProto)
        assert not isinstance(ExtraPosOnly(), VarKeyProto)
        assert not isinstance(ExtraPosOnly(), VarBothProto)

        assert not isinstance(ExtraPosOrKey(), NoVarProto)
        assert isinstance(ExtraPosOrKey(), VarPosProto)
        assert isinstance(ExtraPosOrKey(), VarKeyProto)
        assert isinstance(ExtraPosOrKey(), VarBothProto)

        assert not isinstance(ExtraKeyOnly(), NoVarProto)
        assert not isinstance(ExtraKeyOnly(), VarPosProto)
        assert isinstance(ExtraKeyOnly(), VarKeyProto)
        assert isinstance(ExtraKeyOnly(), VarBothProto)

    def test_pos_only_params(self):
        class PosOnlyProto(AnnotationProtocol):
            @staticmethod
            def f(x: int, /, *args):
                ...

        class PosOrKeyProto(AnnotationProtocol):
            @staticmethod
            def f(x: int, *args):
                ...

        class ExtraPosOnly:
            @staticmethod
            def f(x: int, extra_pos_only: int, /):
                ...

        class ExtraPosOrKey:
            @staticmethod
            def f(x: int, extra_pos_or_key: int):
                ...

        assert isinstance(ExtraPosOnly(), PosOnlyProto)
        assert not isinstance(ExtraPosOnly(), PosOrKeyProto)
        assert isinstance(ExtraPosOrKey(), PosOnlyProto)
        assert isinstance(ExtraPosOrKey(), PosOrKeyProto)

    def test_renamed_params(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, *, key_only: int):
                ...

        class RenamePosOnly:
            @staticmethod
            def f(renamed_pos_only: int, /, pos_or_key: int, *, key_only: int):
                ...

        class RenamePosOrKey:
            @staticmethod
            def f(pos_only: int, /, renamed_pos_or_key: int, *, key_only: int):
                ...

        class RenameKeyOnly:
            @staticmethod
            def f(pos_only: int, /, pos_or_key: int, *, renamed_key_only: int):
                ...

        assert isinstance(RenamePosOnly(), Proto)
        assert not isinstance(RenamePosOrKey(), Proto)
        assert not isinstance(RenameKeyOnly(), Proto)

    def test_simple_annotations(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def no_annotation(x):
                ...

            @staticmethod
            def any_annotation(x: Any):
                ...

            @staticmethod
            def int_annotation(x: int):
                ...

        class ExactMatch:
            @staticmethod
            def no_annotation(x):
                ...

            @staticmethod
            def any_annotation(x: Any):
                ...

            @staticmethod
            def int_annotation(x: int):
                ...

        class ExtraAnnotations:
            @staticmethod
            def no_annotation(x: int):
                ...

            @staticmethod
            def any_annotation(x: int):
                ...

            @staticmethod
            def int_annotation(x: int):
                ...

        class DifferentReturn:
            def no_annotation(x) -> str:
                ...

            @staticmethod
            def any_annotation(x: Any) -> str:
                ...

            @staticmethod
            def int_annotation(x: int) -> str:
                ...

        class Mismatch(ExactMatch):
            @staticmethod
            def int_annotation(x: str):
                ...

        class MatchInParent(ExactMatch):
            pass

        class MismatchInParent(Mismatch):
            pass

        assert isinstance(ExactMatch(), Proto)
        assert isinstance(ExtraAnnotations(), Proto)
        assert isinstance(DifferentReturn(), Proto)
        assert not isinstance(Mismatch(), Proto)
        assert isinstance(MatchInParent(), Proto)
        assert not isinstance(MismatchInParent(), Proto)

    def test_callable_anotations(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(x: Callable[[list, str], int]):
                ...

        class Match:
            @staticmethod
            def f(x: Callable[[list, str], int]):
                ...

        class Nonspecific:
            @staticmethod
            def f(x: Callable):
                ...

        class Mismatch:
            @staticmethod
            def f(x: Callable[[str, list], int]):
                ...

        assert isinstance(Match(), Proto)
        assert not isinstance(Nonspecific(), Proto)
        assert not isinstance(Mismatch(), Proto)

    def test_dict_annotations(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(x: dict[tuple[list, str], int]):
                ...

        class Match:
            @staticmethod
            def f(x: dict[tuple[list, str], int]):
                ...

        class Nonspecific:
            @staticmethod
            def f(x: dict):
                ...

        class Different:
            @staticmethod
            def f(x: dict):
                ...

        class Mismatch:
            @staticmethod
            def f(x: dict[tuple, int]):
                ...

        assert isinstance(Match(), Proto)
        assert not isinstance(Nonspecific(), Proto)
        assert not isinstance(Different(), Proto)
        assert not isinstance(Mismatch(), Proto)

    def test_union_annotations(self):
        class SimpleProto(AnnotationProtocol):
            @staticmethod
            def f(x: int):
                ...

        class UnionProto(AnnotationProtocol):
            @staticmethod
            def f(x: int | str | list):
                ...

        class Simple:
            @staticmethod
            def f(x: int):
                ...

        class SubsetUnion:
            @staticmethod
            def f(x: int | str):
                ...

        class MatchUnion:
            @staticmethod
            def f(x: int | str | list):
                ...

        class SupersetUnion:
            @staticmethod
            def f(x: int | str | list | tuple):
                ...

        class MismatchUnion:
            @staticmethod
            def f(x: tuple | dict):
                ...

        assert isinstance(Simple(), SimpleProto)
        assert not isinstance(MatchUnion(), SimpleProto)
        assert not isinstance(MismatchUnion(), SimpleProto)

        assert isinstance(Simple(), UnionProto)
        assert isinstance(SubsetUnion(), UnionProto)
        assert isinstance(MatchUnion(), UnionProto)
        assert not isinstance(SupersetUnion(), UnionProto)
        assert not isinstance(MismatchUnion(), UnionProto)

    def test_return_anotation(self):
        class IntProto(AnnotationProtocol):
            @staticmethod
            def f() -> int:
                ...

        class NoneProto(AnnotationProtocol):
            @staticmethod
            def f() -> None:
                ...

        class AnyProto(AnnotationProtocol):
            @staticmethod
            def f() -> Any:
                ...

        class UntypedProto(AnnotationProtocol):
            @staticmethod
            def f():
                ...

        class StrReturn:
            @staticmethod
            def f() -> str:
                ...

        class AnyReturn:
            @staticmethod
            def f() -> Any:
                ...

        assert not isinstance(StrReturn(), IntProto)
        assert isinstance(StrReturn(), NoneProto)
        assert isinstance(StrReturn(), AnyProto)
        assert isinstance(StrReturn(), UntypedProto)
        assert isinstance(AnyReturn(), IntProto)

    def test_works_for_classes(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f() -> int:
                ...

        class Test:
            @staticmethod
            def f() -> int:
                ...

        assert isinstance(Test(), Proto)
        assert isinstance(Test, Proto)
