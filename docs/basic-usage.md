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

# Add to a specific namespace and subset
prompt = store.add(
    name="example",
    content="This is a prompt for {{purpose}}",
    namespace="project1",
    description="Code generation prompt",
    tags=["coding", "generation"],
    subset="subproject1"
)
```

### Prompt management

The prompts will be stored in the following structure:

```prompts/
└── namespace/
    └── name/
        └── subset/
            └── subproject1.md
```

If no namespace is provided, the prompt will be stored in the `default` namespace. If no subset is provided, the prompt will be stored directly under the prompt name.

On top of the markdown file, a YAML front matter is included with metadata about the prompt, including its UUID, version, tags, and variables.

### Retrieving Prompts

```python
# Get by name and namespace
prompt = store.get("namespace/name@subset")

# Get an specific version
old_version = store.get("namespace/name@subset", version=1)

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
