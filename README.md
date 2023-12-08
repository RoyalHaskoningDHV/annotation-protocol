# annotation-protocol

The `AnnotationProtocol` allows for more thorough `isinstance` checks in python. Specifically, it adds the following functionality beyond `typing.Protocol`.

1. Check that all attributes from `protocol` are present in the class `other`.
2. Attributes, input arguments and return arguments need ot have the same type annotations between `protocol` and `other`.

Author: [Royal HaskoningDHV](https://global.royalhaskoningdhv.com/)

Email: [ruud.kassing@rhdhv.com](mailto:ruud.kassing@rhdhv.com), [jesse.de.ruijter@rhdhv.com](mailto:jesse.de.ruijter@rhdhv.com), [miguel.hernandez@rhdhv.com](mailto:miguel.hernandez@rhdhv.com), [steffen.burgers@rhdhv.com](mailto:steffen.burgers@rhdhv.com), [pierpaolo.lucarelli@rhdhv.com](mailto:pierpaolo.lucarelli@rhdhv.com)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install **annotation-protocol**.

```bash
pip install annotation-protocol
```

## Usage

You can run `isinstance(other, protocol)` to check if the class `other` adheres to the _Protocol_ of type `AnnotationProtocol`. `protocol` can be a child of `AnnotationProtocol`.

```python
from annotation_protocol import AnnotationProtocol

class TestProtocol(AnnotationProtocol):
    attr: int

    def testfun(a: int, b: str | list) -> set:
        ...

class Other:
    attr: int = 1

    def testfun(a: int, b: str) -> set:
        return {}

print(isinstance(Other, TestProtocol))
```

Note that it is possible to have a subset of type annotations in the `Other` class compared to the `TestProtocol`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
