# Changelog

## Version 1.3.0
- Add docstrings and README.md
- Make sure we allow a subset of annotations in the `other` class compared to `protocol`, but not
  the other way around.
- Refactor code into sub-functions and modules

## Version 1.2.0
- Compare signatures as types not as strings of types in all cases (irrespective of python version)
- Make logging slightly more verbose

## Version 1.1.0
- Use `==` instead of `is` when checking equality of `return_annotation`s in `_compare_annotations`.
- Make logging slightly more verbose

## Version 1.0.0
- Initial public version.
