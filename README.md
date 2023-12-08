# annotation-protocol
The AnnotationProtocol class extends the `isinstance` check of python to be more strict and assess the following in addition to whether the `object` is an instance of the `classinfo` argument.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install **semantic_versioning**.

```bash
pip install semantic_versioning
```

## Usage
Use **validate** function to check if versions in strings are correctly formatted.

```python
from semantic_versioning import SemanticVersion

# use to validate (returns True)
assert SemanticVersion.validate("3.4.5-dev1")
```


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
