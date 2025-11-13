import re
import uuid as uuid_module
from typing import List, Optional

import yaml
from jinja2 import Environment, Template, meta


class Prompt:
    def __init__(
        self,
        content: str,
        version: int,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        subset: Optional[str] = None,
        timestamp: Optional[str] = None,
        uuid: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ):
        self.uuid = uuid or str(uuid_module.uuid4())
        self.name = name
        self.namespace = namespace
        self.content = content
        self.description = description
        self.version = version
        self.tags = tags or []
        self.subset = subset
        self.timestamp = timestamp
        self.created_at = created_at
        self.updated_at = updated_at
        try:
            self._template = Template(content)
        except Exception as e:
            raise ValueError(f"Invalid Jinja2 template: {e}") from e
        self.variables = self._extract_variables(content)

    @property
    def identifier(self) -> str:
        """Get HuggingFace-style identifier."""
        if not self.namespace or not self.name:
            return self.uuid

        base = f"{self.namespace}/{self.name}"
        if self.subset:
            base += f"@{self.subset}"
        return base

    def fill(self, variables: dict) -> str:
        """Fill the prompt template with provided variables."""
        return self._template.render(**variables)

    def _extract_variables(self, content: str) -> List[str]:
        """Extract variable names from the template content."""
        env = Environment()
        ast = env.parse(content)
        variables = meta.find_undeclared_variables(ast)
        return sorted(list(variables))  # Convert set to sorted list

    def get_variables(self) -> List[str]:
        """Return the list of variable names in the template."""
        return self.variables

    def _highlight_variables(self, content: str) -> str:
        """Highlight Jinja2 variables in markdown format."""
        pattern = r'(\{\{[^}]+\}\})'
        return re.sub(pattern, r'**`\1`**', content)

    @staticmethod
    def _unhighlight_variables(content: str) -> str:
        """Remove markdown highlighting from Jinja2 variables."""
        pattern = r'\*\*`(\{\{[^}]+\}\})`\*\*'
        return re.sub(pattern, r'\1', content)

    def to_markdown(self) -> str:
        """Export prompt as Markdown with YAML frontmatter."""
        frontmatter = {
            "uuid": self.uuid,
            "name": self.name,
            "namespace": self.namespace,
            "description": self.description,
            "version": self.version,
            "tags": self.tags,
            "variables": self.variables,
        }

        if self.subset:
            frontmatter["subset"] = self.subset
        if self.created_at:
            frontmatter["created_at"] = self.created_at
        if self.updated_at:
            frontmatter["updated_at"] = self.updated_at

        # Remove None values
        frontmatter = {k: v for k, v in frontmatter.items() if v is not None}

        yaml_str = yaml.dump(
            frontmatter, default_flow_style=False, sort_keys=False
        )

        highlighted_content = self._highlight_variables(self.content)

        return f"---\n{yaml_str}---\n\n{highlighted_content}"

    @classmethod
    def from_markdown(cls, markdown_content: str) -> "Prompt":
        """Create prompt from Markdown with YAML frontmatter."""
        if not markdown_content.startswith("---"):
            raise ValueError(
                "Markdown content must start with YAML frontmatter"
            )

        parts = markdown_content.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Invalid frontmatter format")

        frontmatter = yaml.safe_load(parts[1])
        if frontmatter is None:
            raise ValueError("Empty frontmatter")
        content = parts[2].strip()

        content = cls._unhighlight_variables(content)

        return cls(
            uuid=frontmatter.get("uuid"),
            name=frontmatter.get("name"),
            namespace=frontmatter.get("namespace"),
            content=content,
            description=frontmatter.get("description"),
            version=frontmatter.get("version", 1),
            tags=frontmatter.get("tags", []),
            subset=frontmatter.get("subset"),
            created_at=frontmatter.get("created_at"),
            updated_at=frontmatter.get("updated_at"),
        )
