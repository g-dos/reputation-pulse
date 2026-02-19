import pytest

from reputation_pulse.errors import InvalidHandleError
from reputation_pulse.handles import normalize_handle


def test_normalize_handle_removes_at_prefix():
    assert normalize_handle(" @g-dos ") == "g-dos"


def test_normalize_handle_rejects_blank():
    with pytest.raises(InvalidHandleError):
        normalize_handle("   ")
