from pathlib import Path
import json
import uuid
from typing import List, Dict, Optional, Union, Iterator
from datetime import datetime
from jinja2 import Template
from .prompt import Prompt
from .exceptions import PromptNotFoundError, ReadOnlyStoreError


class PromptStore:
    def __init__(self, location: Union[str, Path], readonly: bool = False):
        """Initialize a new PromptStore.

        Args:
            location: Path to the directory where prompts will be stored
            readonly: If True, the store will be read-only
        """
        self.location = Path(location)
        self.readonly = readonly
        self.index_path = self.location / "index.json"
        self._init_storage()

    def _init_storage(self):
        """Initialize the storage directory and index."""
        self.location.mkdir(parents=True, exist_ok=True)

        if not self.index_path.exists() and not self.readonly:
            self._save_index({})

    def _load_index(self) -> Dict:
        """Load the prompt index."""
        if not self.index_path.exists():
            return {}
        with open(self.index_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_index(self, index: Dict):
        """Save the prompt index."""
        if self.readonly:
            raise ReadOnlyStoreError("Cannot modify a read-only prompt store")
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, prompts: Dict, readonly: bool = True) -> "PromptStore":
        """Create a PromptStore from a dictionary.

        Args:
            prompts: Dictionary of prompt data
            readonly: If True, the store will be read-only

        Returns:
            PromptStore: A prompt store initialized with the given prompts
        """
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        store = cls(temp_dir, readonly=readonly)

        with open(store.index_path, "w", encoding="utf-8") as f:
            json.dump(prompts, f, indent=2, ensure_ascii=False)

        return store

    @classmethod
    def from_file(cls, path: Union[str, Path], readonly: bool = True) -> "PromptStore":
        """Create a PromptStore from a JSON file.

        Args:
            path: Path to the JSON file containing prompts
            readonly: If True, the store will be read-only

        Returns:
            PromptStore: A prompt store initialized with the prompts from the file
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")

        if path.is_file():
            # If it's a single JSON file
            with open(path, "r", encoding="utf-8") as f:
                prompts = json.load(f)
        else:
            # If it's a directory containing an index.json
            index_path = path / "index.json"
            if not index_path.exists():
                raise FileNotFoundError(f"No index.json found in directory: {path}")
            with open(index_path, "r", encoding="utf-8") as f:
                prompts = json.load(f)

        return cls.from_dict(prompts, readonly=readonly)

    def add(
        self,
        content: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Prompt:
        """Add a new prompt to the store."""
        if self.readonly:
            raise ReadOnlyStoreError("Cannot modify a read-only prompt store")

        prompt_uuid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        prompt_data = {
            "uuid": prompt_uuid,
            "content": content,
            "description": description,
            "version": 1,
            "versions": [
                {
                    "content": content,
                    "description": description,
                    "version": 1,
                    "created_at": now,
                }
            ],
            "tags": tags or [],
            "created_at": now,
            "updated_at": now,
        }

        index = self._load_index()
        index[prompt_uuid] = prompt_data
        self._save_index(index)

        return Prompt(
            uuid=prompt_uuid,
            content=content,
            description=description,
            version=1,
            tags=tags or [],
            timestamp=now,
        )

    def get(self, uuid: str, version: Optional[int] = None) -> Prompt:
        """Retrieve a prompt by its UUID."""
        index = self._load_index()
        if uuid not in index:
            raise PromptNotFoundError(f"Prompt with UUID {uuid} not found")

        prompt_data = index[uuid]

        if version:
            version_data = next(
                (v for v in prompt_data["versions"] if v["version"] == version), None
            )
            if not version_data:
                raise PromptNotFoundError(
                    f"Version {version} of prompt {uuid} not found"
                )
            content = version_data["content"]
            description = version_data["description"]
            timestamp = version_data["created_at"]
        else:
            content = prompt_data["content"]
            description = prompt_data["description"]
            timestamp = prompt_data["updated_at"]

        return Prompt(
            uuid=uuid,
            content=content,
            description=description,
            version=prompt_data["version"],
            tags=prompt_data["tags"],
            timestamp=timestamp,
        )

    def find(self, query: str, field: str = "description") -> List[Prompt]:
        """Search for prompts based on a query."""
        if field not in ("description", "content", "tags"):
            raise ValueError("Field must be 'description', 'content', or 'tags'")

        index = self._load_index()
        prompts = []

        for uuid, data in index.items():
            if field == "tags":
                if any(query.lower() in tag.lower() for tag in data["tags"]):
                    prompts.append(self._data_to_prompt(uuid, data))
            else:
                value = data.get(field, "")
                if value and query.lower() in value.lower():
                    prompts.append(self._data_to_prompt(uuid, data))

        return prompts

    def _data_to_prompt(self, uuid: str, data: Dict) -> Prompt:
        """Convert raw data to a Prompt object."""
        return Prompt(
            uuid=uuid,
            content=data["content"],
            description=data["description"],
            version=data["version"],
            tags=data["tags"],
            timestamp=data["updated_at"],
        )

    def merge(self, other: "PromptStore", override: bool = False):
        """Merge another PromptStore into this one."""
        if self.readonly:
            raise ReadOnlyStoreError("Cannot modify a read-only prompt store")

        our_index = self._load_index()
        their_index = other._load_index()

        for uuid, their_data in their_index.items():
            if uuid not in our_index or override:
                our_index[uuid] = their_data

        self._save_index(our_index)

    def __iter__(self) -> Iterator[Prompt]:
        """Iterate over all prompts in the store."""
        index = self._load_index()
        for uuid, data in index.items():
            yield self._data_to_prompt(uuid, data)
