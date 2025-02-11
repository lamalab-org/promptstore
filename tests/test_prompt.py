from promptstore.prompt import Prompt


def test_prompt_fill():
    """Test filling a prompt template."""
    prompt = Prompt(
        uuid="test-uuid",
        content="Hello {{name}}!",
        version=1,
        description="Greeting prompt",
    )

    filled = prompt.fill({"name": "World"})
    assert filled == "Hello World!"


def test_prompt_fill_complex():
    """Test filling a prompt with multiple variables."""
    prompt = Prompt(
        uuid="test-uuid",
        content="Write a {{language}} function that {{task}}",
        version=1,
        description="Code generation prompt",
    )

    filled = prompt.fill(
        {"language": "Python", "task": "sorts a list in reverse order"}
    )
    assert filled == "Write a Python function that sorts a list in reverse order"


def test_prompt_attributes():
    """Test prompt attributes are set correctly."""
    tags = ["test", "example"]
    prompt = Prompt(
        uuid="test-uuid",
        content="test content",
        version=1,
        description="test description",
        tags=tags,
        timestamp="2024-02-11T10:00:00",
    )

    assert prompt.uuid == "test-uuid"
    assert prompt.content == "test content"
    assert prompt.description == "test description"
    assert prompt.version == 1
    assert prompt.tags == tags
    assert prompt.timestamp == "2024-02-11T10:00:00"
