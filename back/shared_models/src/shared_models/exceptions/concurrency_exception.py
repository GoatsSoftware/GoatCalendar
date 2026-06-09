class ConcurrencyException(Exception):
    """
    Raised when an optimistic concurrency control check detects a stale update.

    :param message: The human-readable description of the concurrency conflict.
    """

