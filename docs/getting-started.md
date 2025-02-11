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

# Create a new store
store = PromptStore("./prompts")

# Add a prompt
prompt = store.add(
    content="Explain {{concept}} in simple terms",
    description="Simplification prompt",
    tags=["explanation", "simplification"]
)

# Use the prompt
explanation = prompt.fill({"concept": "quantum computing"})
```

## Next Steps

Check out the [User Guide](guide/basic-usage.md) for more detailed information about using PromptStore.