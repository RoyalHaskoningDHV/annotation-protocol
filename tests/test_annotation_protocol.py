import unittest
from typing import Any, Callable, Dict, Tuple, Union

from annotation_protocol import AnnotationProtocol


class TestAnnotationProtocol(unittest.TestCase):
    def test_missing_callable_attr(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(x):
                ...

        class Missing:
            pass

        self.assertNotIsInstance(Missing(), Proto)

    def test_missing_data_attr(self):
        class Proto(AnnotationProtocol):
            data: int

        class OnlyAfterInit:
            def __init__(self):
                self.data = 123

        self.assertNotIsInstance(OnlyAfterInit, Proto)
        self.assertIsInstance(OnlyAfterInit(), Proto)

    def test_not_a_callable(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(x: int):
                ...

        class NotACallable:
            f: int

        self.assertNotIsInstance(NotACallable(), Proto)

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

        self.assertNotIsInstance(MissingPosOnly(), Proto)
        self.assertNotIsInstance(MissingPosOrKey(), Proto)
        self.assertNotIsInstance(MissingKeyOnly(), Proto)

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

        self.assertIsInstance(Test(), Proto)
        self.assertNotIsInstance(NoClassMethod(), Proto)

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

        self.assertIsInstance(NoParams(), Proto)
        self.assertNotIsInstance(ExtraParams(), Proto)
        self.assertIsInstance(VarPos(), Proto)
        self.assertIsInstance(VarKey(), Proto)
        self.assertNotIsInstance(BoundMethod(), Proto)

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

        self.assertNotIsInstance(ExtraPosOnly(), NoVarProto)
        self.assertNotIsInstance(ExtraPosOnly(), VarPosProto)
        self.assertNotIsInstance(ExtraPosOnly(), VarKeyProto)
        self.assertNotIsInstance(ExtraPosOnly(), VarBothProto)

        self.assertNotIsInstance(ExtraPosOrKey(), NoVarProto)
        self.assertIsInstance(ExtraPosOrKey(), VarPosProto)
        self.assertIsInstance(ExtraPosOrKey(), VarKeyProto)
        self.assertIsInstance(ExtraPosOrKey(), VarBothProto)

        self.assertNotIsInstance(ExtraKeyOnly(), NoVarProto)
        self.assertNotIsInstance(ExtraKeyOnly(), VarPosProto)
        self.assertIsInstance(ExtraKeyOnly(), VarKeyProto)
        self.assertIsInstance(ExtraKeyOnly(), VarBothProto)

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

        self.assertIsInstance(ExtraPosOnly(), PosOnlyProto)
        self.assertNotIsInstance(ExtraPosOnly(), PosOrKeyProto)
        self.assertIsInstance(ExtraPosOrKey(), PosOnlyProto)
        self.assertIsInstance(ExtraPosOrKey(), PosOrKeyProto)

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

        self.assertIsInstance(RenamePosOnly(), Proto)
        self.assertNotIsInstance(RenamePosOrKey(), Proto)
        self.assertNotIsInstance(RenameKeyOnly(), Proto)

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

        self.assertIsInstance(ExactMatch(), Proto)
        self.assertIsInstance(ExtraAnnotations(), Proto)
        self.assertIsInstance(DifferentReturn(), Proto)
        self.assertNotIsInstance(Mismatch(), Proto)
        self.assertIsInstance(MatchInParent(), Proto)
        self.assertNotIsInstance(MismatchInParent(), Proto)

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

        self.assertIsInstance(Match(), Proto)
        self.assertNotIsInstance(Nonspecific(), Proto)
        self.assertNotIsInstance(Mismatch(), Proto)

    def test_dict_annotations(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f(x: Dict[Tuple[list, str], int]):
                ...

        class Match:
            @staticmethod
            def f(x: Dict[Tuple[list, str], int]):
                ...

        class Nonspecific:
            @staticmethod
            def f(x: Dict):
                ...

        class Different:
            @staticmethod
            def f(x: dict):
                ...

        class Mismatch:
            @staticmethod
            def f(x: Dict[tuple, int]):
                ...

        self.assertIsInstance(Match(), Proto)
        self.assertNotIsInstance(Nonspecific(), Proto)
        self.assertNotIsInstance(Different(), Proto)
        self.assertNotIsInstance(Mismatch(), Proto)

    def test_union_annotations(self):
        class SimpleProto(AnnotationProtocol):
            @staticmethod
            def f(x: int):
                ...

        class UnionProto(AnnotationProtocol):
            @staticmethod
            def f(x: Union[int, str, list]):
                ...

        class Simple:
            @staticmethod
            def f(x: int):
                ...

        class SubsetUnion:
            @staticmethod
            def f(x: Union[int, str]):
                ...

        class MatchUnion:
            @staticmethod
            def f(x: Union[int, str, list]):
                ...

        class SupersetUnion:
            @staticmethod
            def f(x: Union[int, str, list, tuple]):
                ...

        class MismatchUnion:
            @staticmethod
            def f(x: Union[tuple, dict]):
                ...

        self.assertIsInstance(Simple(), SimpleProto)
        self.assertIsInstance(MatchUnion(), SimpleProto)
        self.assertNotIsInstance(MismatchUnion(), SimpleProto)

        self.assertNotIsInstance(Simple(), UnionProto)
        self.assertNotIsInstance(SubsetUnion(), UnionProto)
        self.assertIsInstance(MatchUnion(), UnionProto)
        self.assertIsInstance(SupersetUnion(), UnionProto)
        self.assertNotIsInstance(MismatchUnion(), UnionProto)

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

        self.assertNotIsInstance(StrReturn(), IntProto)
        self.assertIsInstance(StrReturn(), NoneProto)
        self.assertIsInstance(StrReturn(), AnyProto)
        self.assertIsInstance(StrReturn(), UntypedProto)
        self.assertIsInstance(AnyReturn(), IntProto)

    def test_works_for_classes(self):
        class Proto(AnnotationProtocol):
            @staticmethod
            def f() -> int:
                ...

        class Test:
            @staticmethod
            def f() -> int:
                ...

        self.assertIsInstance(Test(), Proto)
        self.assertIsInstance(Test, Proto)
