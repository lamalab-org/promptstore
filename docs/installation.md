# Installation

## Requirements

- Python 3.8 or higher
- Jinja2

## Installation Methods

=== "pip"
    ```bash
    pip install promptstore
    ```

=== "uv"
    ```bash
    uv pip install promptstore
    ```

=== "Development"
    ```bash
    git clone https://github.com/lamalab/promptstore
    cd promptstore
    uv pip install -e ".[dev]"
    ```

## Verifying Installation

You can verify your installation by running:

```python
from promptstore import PromptStore
print(PromptStore)  # Should print the class location
```