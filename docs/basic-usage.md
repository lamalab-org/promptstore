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
```