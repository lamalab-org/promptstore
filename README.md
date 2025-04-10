[![Tests](https://github.com/lamalab-org/promptstore/actions/workflows/test.yml/badge.svg)](https://github.com/lamalab-org/promptstore/actions/workflows/test.yml)

# PromptStore

A lightweight Python package for managing and versioning LLM prompt templates.

## Features

- Simple JSON-based storage
- Template versioning
- Tag-based organization
- Jinja2 template syntax
- Package integration utilities

## Installation

```bash
pip install promptstore
```

## Usage

```python
from promptstore import PromptStore

# Create a store
store = PromptStore("./prompts")

# Add a prompt template
prompt = store.add(
    content="Write a {{language}} function that {{task}}",
    description="Code generation prompt",
    tags=["coding", "generation"]
)

# Use the prompt
filled = prompt.fill({
    "language": "Python",
    "task": "sorts a list in reverse order"
})
```

## Documentation

Full documentation is available at [lamalab-org.github.io/promptstore](https://lamalab-org.github.io/promptstore/).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
