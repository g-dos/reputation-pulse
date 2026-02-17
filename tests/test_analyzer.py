import pytest

from reputation_pulse.analyzer import ReputationAnalyzer
from reputation_pulse.errors import InvalidHandleError


@pytest.mark.asyncio
async def test_analyzer_rejects_empty_handle():
    analyzer = ReputationAnalyzer()
    with pytest.raises(InvalidHandleError):
        await analyzer.run("   ")
