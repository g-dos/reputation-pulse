class ReputationPulseError(Exception):
    """Base error for domain failures."""


class InvalidHandleError(ReputationPulseError):
    """Raised when input handle is empty or malformed."""


class CollectorError(ReputationPulseError):
    """Raised when a collector request fails unexpectedly."""


class UpstreamNotFoundError(CollectorError):
    """Raised when upstream resource is not found."""


class UpstreamRateLimitError(CollectorError):
    """Raised when upstream API rate-limits requests."""
