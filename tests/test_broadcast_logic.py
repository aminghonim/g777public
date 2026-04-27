import pytest
import asyncio
from unittest.mock import MagicMock, patch

def test_broadcast_delay_logic():
    """
    TDD Phase 2: Verify that start_broadcast respects the delay range 
    and emits the correct sequence of logs.
    Using anyio for async test execution since pytest-asyncio is not pre-installed.
    """
    from backend.services.group_sender_service import GroupSenderService
    from backend.core.event_broker import event_broker
    import anyio

    async def run_test():
        # Setup
        service = GroupSenderService(instance_name="test_instance")
        group_ids = ["group1", "group2", "group3"]
        message = "Hello World"
        delay_min = 1
        delay_max = 2
        
        # Mock asyncio.sleep to verify calls without actual waiting
        with patch("asyncio.sleep", new_callable=MagicMock) as mock_sleep:
            # Mock event_broker.publish_log
            with patch.object(event_broker, "publish_log", new_callable=MagicMock) as mock_publish:
                async def async_mock(*args, **kwargs):
                    return
                mock_publish.side_effect = async_mock
                mock_sleep.side_effect = async_mock

                await service.start_broadcast(
                    group_ids=group_ids,
                    message=message,
                    delay_min=delay_min,
                    delay_max=delay_max
                )
                
                # 1. Verify sequence of sleeps
                # Total sleeps = 3 (latency mock) + 2 (anti-ban delay) = 5
                assert mock_sleep.call_count == 5
                
                # 2. Verify random delay range
                delay_calls = [call.args[0] for call in mock_sleep.call_args_list if call.args[0] >= delay_min]
                assert len(delay_calls) == 2
                for delay in delay_calls:
                    assert delay_min <= delay <= delay_max

                # 3. Verify real-time logs
                last_log = mock_publish.call_args_list[-1].args[0]
                assert "Broadcast complete" in last_log

    anyio.run(run_test, backend="asyncio")
