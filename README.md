# annotation-protocol

The `AnnotationProtocol` allows for more thorough `isinstance` checks in python. Specifically, it adds the following functionality beyond `typing.Protocol`.

1. Check that all attributes from the class `other` that should adhere to the `protocol` are present in it.
2. Attributes, input arguments and return arguments need ot have the same type annotations between `protocol` and `other`.

Author: [Royal HaskoningDHV](https://global.royalhaskoningdhv.com/)

Email: [ruud.kassing@rhdhv.com](mailto:ruud.kassing@rhdhv.com), [jesse.de.ruijter@rhdhv.com](mailto:jesse.de.ruijter@rhdhv.com), [miguel.hernandez@rhdhv.com](mailto:miguel.hernandez@rhdhv.com), [steffen.burgers@rhdhv.com](mailto:steffen.burgers@rhdhv.com), [pierpaolo.lucarelli@rhdhv.com](mailto:pierpaolo.lucarelli@rhdhv.com)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install **annotation-protocol**.

```bash
pip install annotation-protocol
```

## Background

The `Protocol` class from the `typing` package can be used to create templates of classes with specific attributes and methods. We can check if a class adheres to a given _Protocol_ by doing an `isinstance` check of the form `isinstance(MyClass(), MyProtocol)`. The `AnnotationProtocol` extends this functionality by also checking if all type-hints are the same for each attribute, method argument and method output.

## Usage

For clarity, in the examples below we compare the standard `Protocol` from the `typing` package against the `AnnotationProtocol`. Note that only the `AnnotationProtocol` returns `False` when there is a mismatch in type-hints.

```python
from typing import Protocol, runtime_checkable

from annotation_protocol import AnnotationProtocol


@runtime_checkable
class MyProtocol(Protocol):
    def testfun(my_arg: str | list) -> set:
        ...

class MyAnnotationProtocol(AnnotationProtocol):
    def testfun(my_arg: str | list) -> set:
        ...

class ClassShouldPass:
    def testfun(my_arg: str) -> set:
        return set()

class ClassShouldFail:
    def testfun(my_arg: dict) -> set:
        return set()

print(f"Protocol: {isinstance(ClassShouldPass(), MyProtocol)}")  # returns True
print(f"Protocol: {isinstance(ClassShouldFail(), MyProtocol)}")  # returns True

print(f"AnnotationProtocol: {isinstance(ClassShouldPass(), MyAnnotationProtocol)}")  # returns True
print(f"AnnotationProtocol: {isinstance(ClassShouldFail(), MyAnnotationProtocol)}")  # returns False
```

Note that it is possible to have a subset of type annotations in the `ClassShouldPass` class compared to the `MyAnnotationProtocol`. In other words it is not necessary to have all types of a `UnionType` group of types from the protocol in the class that should adhere to the protocol.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
