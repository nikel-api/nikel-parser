# Validation & Data Integrity
This module handles the schemas and validation process for all parsers. Each parser has it's own schema under the `schemas` module.

To validate a JSON output against a particular schema, you can do something like:
```python
from validations.data_validator import DataValidator

d = DataValidator()
d.run_validation(data, schema)   # Raises error, if any
```
while replacing `data` and `schema` with the appropriate objects.