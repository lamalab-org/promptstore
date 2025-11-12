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


def test_markdown_variable_highlighting():
    """Test that variables are highlighted in markdown export and
    unhighlighted on import."""
    # Create a prompt with variables
    prompt = Prompt(
        uuid="test-uuid",
        name="test-prompt",
        namespace="test",
        content="Write a {{language}} function that {{task}}",
        version=1,
        description="Test prompt",
    )

    # Export to markdown - variables should be highlighted
    markdown = prompt.to_markdown()
    assert "**`{{language}}`**" in markdown
    assert "**`{{task}}`**" in markdown

    # Import from markdown - variables should be unhighlighted
    loaded_prompt = Prompt.from_markdown(markdown)
    assert loaded_prompt.content == "Write a {{language}} function that {{task}}"
    assert loaded_prompt.variables == ["language", "task"]

    # Verify it still works for filling
    filled = loaded_prompt.fill({"language": "Python", "task": "sorts a list"})
    assert filled == "Write a Python function that sorts a list"


def test_markdown_roundtrip_with_highlighting():
    """Test that prompts can be exported and imported without data loss."""
    original = Prompt(
        uuid="test-uuid",
        name="test-prompt",
        namespace="test",
        content="Hello {{name}}, your task is {{task}}!",
        version=1,
        description="Test prompt",
        tags=["test", "demo"],
    )

    # Export and re-import
    markdown = original.to_markdown()
    loaded = Prompt.from_markdown(markdown)

    # Verify all data is preserved
    assert loaded.uuid == original.uuid
    assert loaded.name == original.name
    assert loaded.namespace == original.namespace
    assert loaded.content == original.content
    assert loaded.version == original.version
    assert loaded.description == original.description
    assert loaded.tags == original.tags
    assert loaded.variables == original.variables

