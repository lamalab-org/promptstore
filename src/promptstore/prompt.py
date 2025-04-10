from typing import List, Optional

from jinja2 import Environment, Template, meta


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
        self.variables = self._extract_variables(content)

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
