class PromptNotFoundError(Exception):
    """Raised when a prompt with the given UUID is not found."""

    pass


class ReadOnlyStoreError(Exception):
    """Raised when attempting to modify a read-only store."""

    pass
