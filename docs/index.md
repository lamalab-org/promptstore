# PromptStore

A lightweight Python package for managing and versioning LLM prompt templates.

## Features

- Simple JSON-based storage
- Template versioning
- Tag-based organization
- Jinja2 template support
- Package integration utilities
- Easy to extend and customize

## Quick Start

```python
from promptstore import PromptStore

# Create a new store
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

## Why PromptStore?

- **Lightweight**: Minimal dependencies, just Jinja2
- **Simple**: JSON-based storage, easy to inspect and modify
- **Flexible**: Support for both local development and package distribution
- **Versioned**: Track changes to your prompts
- **Organized**: Tag and search your prompts
- **Package-Ready**: Easy to bundle prompts with your package
