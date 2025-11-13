import json
import re
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Union

import pystow

from .exceptions import PromptNotFoundError, ReadOnlyStoreError
from .prompt import Prompt


class PromptStore:
    def __init__(self, location: Union[str, Path], readonly: bool = False):
        """Initialize a new PromptStore.

        Args:
            location: Path to the directory where prompts will be stored
            readonly: If True, the store will be read-only
        """
        self.location = Path(location)
        self.readonly = readonly
        self.promptstore_dir = self.location / ".promptstore"
        self.index_path = self.promptstore_dir / "index.json"
        self.aliases_path = self.promptstore_dir / "aliases.json"
        self._init_storage()

    def _init_storage(self):
        """Initialize the storage directory and index."""
        self.location.mkdir(parents=True, exist_ok=True)
        self.promptstore_dir.mkdir(exist_ok=True)

        if not self.index_path.exists() and not self.readonly:
            self._save_index({})
        if not self.aliases_path.exists() and not self.readonly:
            self._save_aliases({})

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

    def _load_aliases(self) -> Dict:
        """Load the aliases mapping."""
        if not self.aliases_path.exists():
            return {}
        with open(self.aliases_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_aliases(self, aliases: Dict):
        """Save the aliases mapping."""
        if self.readonly:
            raise ReadOnlyStoreError("Cannot modify a read-only prompt store")
        with open(self.aliases_path, "w", encoding="utf-8") as f:
            json.dump(aliases, f, indent=2, ensure_ascii=False)

    def _parse_identifier(self, identifier: str) -> Dict[str, Optional[str]]:
        """Parse HuggingFace-style identifier.

        Format: namespace/name[@subset]

        Returns:
            Dict with keys: namespace, name, subset
        """
        # Check if it's a UUID
        if self._is_uuid(identifier):
            return {
                "uuid": identifier,
                "namespace": None,
                "name": None,
                "subset": None
            }

        # Parse namespace/name[@subset]
        pattern = r'^([^/]+)/([^@]+)(?:@(.+))?$'
        match = re.match(pattern, identifier)

        if not match:
            # If it doesn't match the pattern and is not a UUID,
            # treat it as a potential UUID for backward compatibility
            # This handles cases like "nonexistent-uuid" which might be
            # a malformed UUID that we still want to look up
            return {
                "uuid": identifier,
                "namespace": None,
                "name": None,
                "subset": None
            }

        namespace, name, subset = match.groups()

        return {
            "uuid": None,
            "namespace": namespace,
            "name": name,
            "subset": subset
        }

    def _is_uuid(self, value: str) -> bool:
        """Check if a string is a valid UUID."""
        try:
            uuid.UUID(value)
            return True
        except (ValueError, AttributeError):
            return False

    def _get_prompt_path(
        self,
        namespace: str,
        name: str,
        subset: Optional[str] = None,
        version: Optional[int] = None
    ) -> Path:
        """Get the file path for a prompt.

        Args:
            namespace: The namespace
            name: The prompt name
            subset: Optional subset
            version: Optional version number

        Returns:
            Path to the prompt file
        """
        prompt_dir = self.location / namespace / name

        if subset:
            if version:
                return prompt_dir / "subsets" / f"{subset}_v{version}.md"
            else:
                return prompt_dir / "subsets" / f"{subset}.md"
        elif version:
            return prompt_dir / "versions" / f"v{version}.md"
        else:
            return prompt_dir / "prompt.md"

    def _read_prompt_file(self, file_path: Path) -> Prompt:
        """Read a prompt from a markdown file."""
        if not file_path.exists():
            raise PromptNotFoundError(f"Prompt file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return Prompt.from_markdown(content)

    def _write_prompt_file(self, file_path: Path, prompt: Prompt):
        """Write a prompt to a markdown file."""
        if self.readonly:
            raise ReadOnlyStoreError("Cannot modify a read-only prompt store")

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(prompt.to_markdown())

    @classmethod
    def from_dict(cls, prompts: Dict, readonly: bool = True) -> "PromptStore":
        """Create a PromptStore from a dictionary.

        Args:
            prompts: Dictionary of prompt data (old JSON format)
            readonly: If True, the store will be read-only

        Returns:
            PromptStore: A prompt store initialized with the given prompts
        """
        import tempfile

        temp_dir = Path(tempfile.mkdtemp())
        # Create store as writable first to populate it
        store = cls(temp_dir, readonly=False)

        # Convert old format to new format
        for uuid_val, data in prompts.items():
            # Create a prompt with the old data
            namespace = data.get("namespace", "default")
            name = data.get("name", f"prompt-{uuid_val[:8]}")

            prompt = Prompt(
                uuid=uuid_val,
                name=name,
                namespace=namespace,
                content=data["content"],
                description=data.get("description"),
                version=data.get("version", 1),
                tags=data.get("tags", []),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
            )

            # Save to file system
            file_path = store._get_prompt_path(namespace, name)
            store._write_prompt_file(file_path, prompt)

            # Update index
            index = store._load_index()
            index[uuid_val] = {
                "namespace": namespace,
                "name": name,
                "path": str(file_path.relative_to(store.location))
            }
            store._save_index(index)

            # Update aliases
            aliases = store._load_aliases()
            aliases[f"{namespace}/{name}"] = uuid_val
            store._save_aliases(aliases)

        # Now set to readonly if requested
        store.readonly = readonly
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
            # If it's a single JSON file (old format)
            with open(path, "r", encoding="utf-8") as f:
                prompts = json.load(f)
            return cls.from_dict(prompts, readonly=readonly)
        else:
            # If it's a directory, just use it as the location
            return cls(path, readonly=readonly)

    def add(
        self,
        content: str,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        subset: Optional[str] = None,
    ) -> Prompt:
        """Add a new prompt to the store.

        Args:
            content: The content of the prompt
            name: Name of the prompt (required for new system)
            namespace: Namespace/organization (defaults to 'default')
            description: A description of the prompt
            tags: A list of tags for the prompt
            subset: Optional subset/variant name

        Returns:
            Prompt: The newly created prompt
        """
        if self.readonly:
            raise ReadOnlyStoreError("Cannot modify a read-only prompt store")

        # Set defaults
        if not namespace:
            namespace = "default"
        if not name:
            name = f"prompt-{str(uuid.uuid4())[:8]}"

        prompt_uuid = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        prompt = Prompt(
            uuid=prompt_uuid,
            name=name,
            namespace=namespace,
            content=content,
            description=description,
            version=1,
            tags=tags or [],
            subset=subset,
            created_at=now,
            updated_at=now,
        )

        # Save to file system
        file_path = self._get_prompt_path(namespace, name, subset)
        self._write_prompt_file(file_path, prompt)

        # Update index
        index = self._load_index()
        index[prompt_uuid] = {
            "namespace": namespace,
            "name": name,
            "subset": subset,
            "path": str(file_path.relative_to(self.location))
        }
        self._save_index(index)

        # Update aliases
        aliases = self._load_aliases()
        identifier = f"{namespace}/{name}"
        if subset:
            identifier += f"@{subset}"
        aliases[identifier] = prompt_uuid
        self._save_aliases(aliases)

        return prompt

    def get(
        self,
        identifier: str,
        version: Optional[int] = None,
        subset: Optional[str] = None
    ) -> Prompt:
        """Retrieve a prompt by its identifier or UUID.

        Args:
            identifier: HuggingFace-style identifier (namespace/name[@subset]) or UUID
            version: The version of the prompt to retrieve
            subset: The subset of the prompt to retrieve (overrides identifier)

        Returns:
            Prompt: The prompt object
        """
        parsed = self._parse_identifier(identifier)

        # Handle UUID lookup (backward compatibility)
        if parsed["uuid"]:
            warnings.warn(
                "UUID-based lookup is deprecated. Use 'namespace/name' format.",
                DeprecationWarning,
                stacklevel=2
            )
            return self._get_by_uuid(parsed["uuid"], version)

        # Use parsed values, but allow override by parameters
        namespace = parsed["namespace"]
        name = parsed["name"]
        subset = subset or parsed["subset"]

        # Get the file path and read the prompt
        file_path = self._get_prompt_path(namespace, name, subset, version)
        return self._read_prompt_file(file_path)

    def _get_by_uuid(self, uuid_val: str, version: Optional[int] = None) -> Prompt:
        """Get a prompt by UUID (backward compatibility)."""
        index = self._load_index()
        if uuid_val not in index:
            raise PromptNotFoundError(f"Prompt with UUID {uuid_val} not found")

        entry = index[uuid_val]
        namespace = entry["namespace"]
        name = entry["name"]
        subset = entry.get("subset")

        file_path = self._get_prompt_path(namespace, name, subset, version)
        return self._read_prompt_file(file_path)

    def find(self, query: str, field: str = "description") -> List[Prompt]:
        """Search for prompts based on a query.

        Args:
            query: The search query
            field: The field to search in (description, content, or tags)

        Returns:
            List[Prompt]: A list of prompts matching the query
        """
        if field not in ("description", "content", "tags"):
            raise ValueError("Field must be 'description', 'content', or 'tags'")

        prompts = []
        for prompt in self:
            if field == "tags":
                if any(query.lower() in tag.lower() for tag in prompt.tags):
                    prompts.append(prompt)
            elif field == "description" and prompt.description:
                if query.lower() in prompt.description.lower():
                    prompts.append(prompt)
            elif field == "content":
                if query.lower() in prompt.content.lower():
                    prompts.append(prompt)

        return prompts

    def update(
        self,
        identifier: str,
        content: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Prompt:
        """Update an existing prompt with a new version.

        Args:
            identifier: The identifier or UUID of the prompt to update
            content: New content for the prompt
            description: New description for the prompt
            tags: New tags for the prompt

        Returns:
            Prompt: The updated prompt

        Raises:
            ReadOnlyStoreError: If the store is read-only
            PromptNotFoundError: If the prompt doesn't exist
        """
        if self.readonly:
            raise ReadOnlyStoreError("Cannot modify a read-only prompt store")

        # Get the current prompt
        current = self.get(identifier)

        # Create new version
        now = datetime.now(timezone.utc).isoformat()
        new_version = current.version + 1

        # Save old version to versions directory if it's not already there
        if current.version > 0:
            old_version_path = self._get_prompt_path(
                current.namespace, current.name, current.subset, current.version
            )
            if not old_version_path.exists():
                self._write_prompt_file(old_version_path, current)

        # Create updated prompt
        updated = Prompt(
            uuid=current.uuid,
            name=current.name,
            namespace=current.namespace,
            content=content,
            description=description if description is not None else current.description,
            version=new_version,
            tags=tags if tags is not None else current.tags,
            subset=current.subset,
            created_at=current.created_at,
            updated_at=now,
        )

        # Write new version as the main prompt
        file_path = self._get_prompt_path(
            current.namespace, current.name, current.subset
        )
        self._write_prompt_file(file_path, updated)

        return updated

    def __iter__(self) -> Iterator[Prompt]:
        """Iterate over all prompts in the store."""
        index = self._load_index()
        for _, entry in index.items():
            try:
                file_path = self.location / entry["path"]
                yield self._read_prompt_file(file_path)
            except Exception:
                # Skip prompts that can't be read
                continue

    def merge(self, other: "PromptStore", override: bool = False):
        """Merge another PromptStore into this one.

        Args:
            other: The other PromptStore to merge
            override: If True, override existing prompts with those from the other store

        Raises:
            ReadOnlyStoreError: If the store is read-only
        """
        if self.readonly:
            raise ReadOnlyStoreError("Cannot modify a read-only prompt store")

        for prompt in other:
            identifier = f"{prompt.namespace}/{prompt.name}"
            if prompt.subset:
                identifier += f"@{prompt.subset}"

            try:
                self.get(identifier)
                if override:
                    self.update(
                        identifier,
                        content=prompt.content,
                        description=prompt.description,
                        tags=prompt.tags,
                    )
            except PromptNotFoundError:
                # Doesn't exist, add it
                self.add(
                    content=prompt.content,
                    name=prompt.name,
                    namespace=prompt.namespace,
                    description=prompt.description,
                    tags=prompt.tags,
                    subset=prompt.subset,
                )

    def get_online(
        self, uuid: str, url: str, version: int | None = None, folder: str = "prompts"
    ) -> Prompt:
        """Retrieve a prompt by its UUID from an online store.

        Args:
            uuid: The UUID of the prompt to retrieve
            url: The URL of the online store
            version: The version of the prompt to retrieve
            folder: The folder name to use for caching (defaults to "prompts")

        Returns:
            Prompt: The prompt object

        Raises:
            PromptNotFoundError: If the prompt with the given UUID doesn't exist
        """
        data = pystow.ensure_json(folder, url=url)

        if uuid not in data:
            raise PromptNotFoundError(
                f"Prompt with UUID {uuid} not found in online store"
            )

        prompt_data = data[uuid]

        if version:
            version_data = next(
                (v for v in prompt_data["versions"] if v["version"] == version), None
            )
            if not version_data:
                raise PromptNotFoundError(
                    f"Version {version} of prompt {uuid} not found in online store"
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
