# PromptStore

A lightweight Python package for managing and versioning LLM prompt templates.

## Features

- Simple JSON-based storage
- Template versioning
- Tag-based organization
- Jinja2 template support
- **Variable highlighting** in Markdown exports
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

This automatically generates a markdown representation like this:

```markdown
---
uuid: 77a6b015-efea-436e-8636-6ae06c438ad8
name: example
namespace: project1
description: Code generation prompt
version: 1
tags:
- coding
- generation
variables:
- language
- task
subset: subproject1
created_at: '2025-11-12T11:17:24.128334+00:00'
updated_at: '2025-11-12T11:17:24.128334+00:00'
---

Write a **`{{language}}`** function that **`{{task}}`**

This makes it easy to identify which parts of the prompt are variables when viewing the markdown files.

## Why PromptStore?

- **Lightweight**: Minimal dependencies, just Jinja2
- **Simple**: JSON-based storage, easy to inspect and modify
- **Flexible**: Support for both local development and package distribution
- **Versioned**: Track changes to your prompts
- **Organized**: Tag and search your prompts
- **Package-Ready**: Easy to bundle prompts with your package
