from typing import List, Optional
from jinja2 import Template


class Prompt:
    def __init__(
        self,
        uuid: str,
        content: str,
        version: int,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        timestamp: Optional[str] = None,
    ):
        self.uuid = uuid
        self.content = content
        self.description = description
        self.version = version
        self.tags = tags or []
        self.timestamp = timestamp
        self._template = Template(content)

    def fill(self, variables: dict) -> str:
        """Fill the prompt template with provided variables."""
        return self._template.render(**variables)
