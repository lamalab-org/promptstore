import pytest

from promptstore import PromptStore
from promptstore.exceptions import PromptNotFoundError, ReadOnlyStoreError


def test_store_initialization(temp_store_dir):
    """Test that store initializes correctly."""
    store = PromptStore(temp_store_dir)
    assert store.location == temp_store_dir
    assert store.index_path.exists()
    assert not store.readonly


def test_add_prompt(store, sample_prompts):
    """Test adding a prompt to the store."""
    data = sample_prompts["code-gen"]
    prompt = store.add(
        content=data["content"], description=data["description"], tags=data["tags"]
    )

    assert prompt.content == data["content"]
    assert prompt.description == data["description"]
    assert set(prompt.tags) == set(data["tags"])
    assert prompt.version == 1


def test_get_prompt(store, sample_prompts):
    """Test retrieving a prompt by UUID."""
    data = sample_prompts["code-gen"]
    added = store.add(
        content=data["content"], description=data["description"], tags=data["tags"]
    )

    retrieved = store.get(added.uuid)
    assert retrieved.uuid == added.uuid
    assert retrieved.content == added.content
    assert retrieved.description == added.description
    assert set(retrieved.tags) == set(added.tags)


def test_get_nonexistent_prompt(store):
    """Test that getting a nonexistent prompt raises an error."""
    with pytest.raises(PromptNotFoundError):
        store.get("nonexistent-uuid")


def test_find_prompts(store, sample_prompts):
    """Test searching for prompts."""
    # Add both sample prompts
    for data in sample_prompts.values():
        store.add(
            content=data["content"], description=data["description"], tags=data["tags"]
        )

    # Search by description
    coding_prompts = store.find("code", field="description")
    assert len(coding_prompts) == 1
    assert coding_prompts[0].description == sample_prompts["code-gen"]["description"]

    # Search by content
    summarize_prompts = store.find("summarize", field="content")
    assert len(summarize_prompts) == 1
    assert summarize_prompts[0].content == sample_prompts["summarize"]["content"]


def test_readonly_store(temp_store_dir):
    """Test that readonly store prevents modifications."""
    # First create a writable store with some data
    store = PromptStore(temp_store_dir)
    prompt = store.add(content="test content", description="test description")

    # Then create a readonly store at the same location
    readonly_store = PromptStore(temp_store_dir, readonly=True)

    # Should be able to read
    assert readonly_store.get(prompt.uuid).content == "test content"

    # But not write
    with pytest.raises(ReadOnlyStoreError):
        readonly_store.add(content="new content", description="new description")


def test_from_dict():
    """Test creating store from dictionary."""
    prompts = {
        "test-uuid": {
            "uuid": "test-uuid",
            "content": "test content",
            "description": "test description",
            "version": 1,
            "tags": ["test"],
            "versions": [
                {
                    "content": "test content",
                    "description": "test description",
                    "version": 1,
                    "created_at": "2024-02-11T10:00:00",
                }
            ],
            "created_at": "2024-02-11T10:00:00",
            "updated_at": "2024-02-11T10:00:00",
        }
    }

    store = PromptStore.from_dict(prompts)
    prompt = store.get("test-uuid")
    assert prompt.content == "test content"
    assert prompt.description == "test description"
    assert prompt.tags == ["test"]


def test_add_with_namespace_and_name(store):
    """Test adding a prompt with explicit namespace and name."""
    prompt = store.add(
        content="test content",
        name="my-prompt",
        namespace="myorg",
        description="test description",
    )

    assert prompt.name == "my-prompt"
    assert prompt.namespace == "myorg"
    assert prompt.identifier == "myorg/my-prompt"


def test_get_by_identifier(store):
    """Test retrieving a prompt using HuggingFace-style identifier."""
    added = store.add(
        content="test content",
        name="my-prompt",
        namespace="myorg",
        description="test description",
    )

    # Retrieve by identifier
    retrieved = store.get("myorg/my-prompt")
    assert retrieved.uuid == added.uuid
    assert retrieved.content == added.content
    assert retrieved.name == "my-prompt"
    assert retrieved.namespace == "myorg"


def test_add_with_subset(store):
    """Test adding a prompt with a subset."""
    prompt = store.add(
        content="test content for python",
        name="code-gen",
        namespace="myorg",
        subset="python",
        description="Python code generator",
    )

    assert prompt.subset == "python"
    assert prompt.identifier == "myorg/code-gen@python"


def test_get_by_identifier_with_subset(store):
    """Test retrieving a prompt with subset using identifier."""
    added = store.add(
        content="test content for python",
        name="code-gen",
        namespace="myorg",
        subset="python",
        description="Python code generator",
    )

    # Retrieve by identifier with subset
    retrieved = store.get("myorg/code-gen@python")
    assert retrieved.uuid == added.uuid
    assert retrieved.subset == "python"


def test_update_creates_version(store):
    """Test that updating a prompt creates a new version."""
    added = store.add(
        content="original content",
        name="my-prompt",
        namespace="myorg",
        description="original description",
    )

    assert added.version == 1

    # Update the prompt
    updated = store.update(
        "myorg/my-prompt",
        content="updated content",
        description="updated description",
    )

    assert updated.version == 2
    assert updated.content == "updated content"
    assert updated.description == "updated description"
    assert updated.uuid == added.uuid  # Same UUID


def test_markdown_persistence(store):
    """Test that prompts are persisted as markdown files."""
    added = store.add(
        content="test content",
        name="my-prompt",
        namespace="myorg",
        description="test description",
        tags=["test", "example"],
    )

    # Check that the markdown file exists
    prompt_path = store.location / "myorg" / "my-prompt" / "prompt.md"
    assert prompt_path.exists()

    # Read the file and verify it's markdown with frontmatter
    with open(prompt_path, "r") as f:
        content = f.read()

    assert content.startswith("---")
    assert "name: my-prompt" in content
    assert "namespace: myorg" in content
    assert "test content" in content
    assert added.uuid in content  # UUID should be in frontmatter


def test_to_markdown_and_from_markdown(store):
    """Test that prompts can be serialized and deserialized to/from markdown."""
    from promptstore.prompt import Prompt

    # Create a prompt
    original = Prompt(
        name="test-prompt",
        namespace="test",
        content="test content with {{variable}}",
        description="test description",
        version=1,
        tags=["tag1", "tag2"],
    )

    # Convert to markdown
    markdown = original.to_markdown()

    # Convert back from markdown
    restored = Prompt.from_markdown(markdown)

    assert restored.name == original.name
    assert restored.namespace == original.namespace
    assert restored.content == original.content
    assert restored.description == original.description
    assert restored.version == original.version
    assert restored.tags == original.tags
    assert restored.uuid == original.uuid
