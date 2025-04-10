import shutil
import tempfile
from pathlib import Path

import pytest
from promptstore import PromptStore


@pytest.fixture
def temp_store_dir():
    """Create a temporary directory for the store."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def store(temp_store_dir):
    """Create a new PromptStore instance."""
    return PromptStore(temp_store_dir)


@pytest.fixture
def sample_prompts():
    """Sample prompt data for testing."""
    return {
        "code-gen": {
            "content": "Write a {{language}} function that {{task}}",
            "description": "Code generation prompt",
            "tags": ["coding", "generation"],
        },
        "summarize": {
            "content": "Summarize the following {{document_type}}: {{content}}",
            "description": "Text summarization prompt",
            "tags": ["summarization", "text"],
        },
    }
