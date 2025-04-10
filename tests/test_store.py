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
