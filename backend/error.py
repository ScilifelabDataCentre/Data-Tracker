"""Custom exceptions."""


class BadIdentification(Exception):
    """Bad user identifier (username/API key)."""


class ForbiddenUpdateInput(Exception):
    """The input contained fields that may not be updated manually."""
