# Getting Started

## Installation

Install promptstore using pip:

```bash
pip install promptstore
```

## Basic Usage

Create a store and add some prompts:

```python
from promptstore import PromptStore

# Create a store
store = PromptStore("./prompts")

# Add a prompt template
prompt = store.add(
    name="example",
    content="Write a {{language}} function that {{task}}",
    namespace="project1",
    description="Code generation prompt",
    tags=["coding", "generation"],
    subset="subproject1"
)

# Use the prompt
filled = prompt.fill({
    "language": "Python",
    "task": "sorts a list in reverse order"
})

# Export to markdown (variables will be highlighted)
markdown = prompt.to_markdown()
print(markdown)
# Output shows: Explain **`{{concept}}`** in simple terms
```

## Variable Highlighting

When you export prompts to markdown, template variables are automatically highlighted with bold code formatting (**`{{variable}}`**), making them stand out visually. This is especially useful when:

- Reviewing prompts in markdown viewers or editors
- Sharing prompts with team members
- Documenting your prompt templates
- Identifying which parts of the prompt need to be filled

The highlighting is automatically removed when loading prompts from markdown, so your templates work seamlessly.

## Next Steps

Check out the [User Guide](guide/basic-usage.md) for more detailed information about using PromptStore.
