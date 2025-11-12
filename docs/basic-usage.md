# Basic Usage

## Creating a Store

```python
from promptstore import PromptStore

# Create a new store
store = PromptStore("./prompts")

# Create a read-only store
readonly_store = PromptStore("./prompts", readonly=True)
```

## Managing Prompts

### Adding Prompts

```python
# Add a simple prompt
prompt = store.add(
    content="Hello, {{name}}!",
    description="Basic greeting",
    tags=["greeting"]
)

# Add a more complex prompt
prompt = store.add(
    content="Write a {{language}} function that {{task}}",
    description="Code generation prompt",
    tags=["coding", "generation"]
)
```

### Retrieving Prompts

```python
# Get by UUID
prompt = store.get("prompt-uuid")

# Get specific version
old_version = store.get("prompt-uuid", version=1)

# Search prompts
coding_prompts = store.find("code", field="description")
```

### Using Prompts

```python
# Fill a prompt template
prompt = store.get("prompt-uuid")
result = prompt.fill({
    "language": "Python",
    "task": "sorts a list in ascending order"
})

# Get list of variables in a prompt
variables = prompt.get_variables()
print(f"Required variables: {variables}")  # ['language', 'task']
```

### Exporting and Importing Prompts

Prompts can be exported to Markdown format with YAML frontmatter. When exported, template variables are automatically highlighted for better visibility:

```python
# Export prompt to markdown
markdown = prompt.to_markdown()
print(markdown)
```

Example output:

```markdown
---
uuid: 6172841b-e296-4d4b-bb32-7b8a074ab36e
name: code-generator
namespace: default
description: Code generation prompt
version: 1
tags:
- coding
- generation
variables:
- language
- task
---

Write a **`{{language}}`** function that **`{{task}}`**
```

Variables are highlighted as **`{{variable}}`** (bold code blocks) in the markdown output, making them visually distinct and easier to identify.

You can also load prompts from markdown:

```python
from promptstore import Prompt

# Load from markdown file
with open("prompt.md", "r") as f:
    markdown_content = f.read()

prompt = Prompt.from_markdown(markdown_content)

# The highlighting is automatically removed when loading
# and the prompt works exactly as before
result = prompt.fill({"language": "Python", "task": "sorts a list"})
```

Similarly, you can use prompts from an online source:

```python
url = "https://raw.githubusercontent.com/awesome-org/prompt-collections/main/prompts.json"
# Using a sample prompt collection hosted on GitHub.
# Fill a prompt template
prompt = store.get_online("prompt-uuid", url)
result = prompt.fill({
    "language": "Python",
    "task": "sorts a list in ascending order"
})
```
