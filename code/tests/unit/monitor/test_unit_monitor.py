from monitor.consumer import check_operation
import pytest


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            {
            "source": 'sensor_switch',
            "deliver_to": 'data_processor',
            "operation": 'process_impuls'
            },
            True
        ),
        (
            {
            "source": 'sensor_switch',
            "deliver_to": 'query_processor',
            "operation": 'apply_impuls'
            },
            False
        ),
        (
            {
            "source": 'commun_user_interf',
            "deliver_to": 'data_processor',
            "operation": 'get_historical_data'
            },
            False
        ),
        (
            {
            "source": 'commun_user_interf',
            "deliver_to": 'query_processor',
            "operation": 'write_new_commands'
            },
            False
        ),
        (
            {
            "source": 'commun_user_interf',
            "deliver_to": 'query_processor',
            "operation": 'get_historical_data'
            },
            True
        ),
        (
            {
            "source": 'commun_prog',
            "deliver_to": 'query_processor',
            "operation": 'write_new_commands'
            },
            True
        ),
        (
            {
            "source": 'commun_prog',
            "deliver_to": 'data_processor',
            "operation": 'get_historical_data'
            },
            False
        ),
        (
            {
            "source": 'commun_prog',
            "deliver_to": 'query_processor',
            "operation": 'get_historical_data'
            },
            True
        ),
        (
            {
            "source": 'query_processor',
            "deliver_to": 'data_processor',
            "operation": 'get_historical_data'
            },
            True
        ),
        (
            {
            "source": 'query_processor',
            "deliver_to": 'data_processor',
            "operation": 'write_new_commands'
            },
            True
        ),
        (
            {
            "source": 'query_processor',
            "deliver_to": 'command_block',
            "operation": 'write_new_commands'
            },
            False
        ),
        (
            {
            "source": 'query_processor',
            "deliver_to": 'commun_prog',
            "operation": 'return_historical_data'
            },
            True
        ),
        (
            {
            "source": 'query_processor',
            "deliver_to": 'commun_prog',
            "operation": 'process_event'
            },
            True
        ),
        (
            {
            "source": 'query_processor',
            "deliver_to": 'commun_user_interf',
            "operation": 'return_historical_data'
            },
            True
        ),
        (
            {
            "source": 'query_processor',
            "deliver_to": 'commun_user_interf',
            "operation": 'high_bpm_alert'
            },
            True
        ),
        (
            {
            "source": 'data_processor',
            "deliver_to": 'storage',
            "operation": 'get_historical_data'
            },
            True
        ),
        (
            {
            "source": 'data_processor',
            "deliver_to": 'storage',
            "operation": 'write_new_data'
            },
            True
        ),
        (
            {
            "source": 'data_processor',
            "deliver_to": 'storage',
            "operation": 'delete_all'
            },
            False
        ),
        (
            {
            "source": 'data_processor',
            "deliver_to": 'command_block',
            "operation": 'return_historical_data'
            },
            True
        ),
        (
            {
            "source": 'data_processor',
            "deliver_to": 'query_processor',
            "operation": 'return_historical_data'
            },
            False
        ),
        (
            {
            "source": 'data_processor',
            "deliver_to": 'command_block',
            "operation": 'apply_impuls'
            },
            True
        ),
        (
            {
            "source": 'data_processor',
            "deliver_to": 'command_block',
            "operation": 'high_bpm_alert'
            },
            True
        ),
        (
            {
            "source": 'data_processor',
            "deliver_to": 'command_block',
            "operation": 'write_new_commands'
            },
            True
        ),
        (
            {
            "source": 'command_block',
            "deliver_to": 'query_processor',
            "operation": 'return_historical_data'
            },
            True
        ),
        (
            {
            "source": 'command_block',
            "deliver_to": 'query_processor',
            "operation": 'commands_committed'
            },
            True
        ),
        (
            {
            "source": 'command_block',
            "deliver_to": 'query_processor',
            "operation": 'fail_commands_save'
            },
            True
        ),
        (
            {
            "source": 'command_block',
            "deliver_to": 'query_processor',
            "operation": 'high_bpm_alert'
            },
            True
        ),
        (
            {
            "source": 'command_block',
            "deliver_to": 'commun_user_interf',
            "operation": 'high_bpm_alert'
            },
            False
        ),
        (
            {
            "source": 'command_block',
            "deliver_to": 'data_processor',
            "operation": 'get_historical_data'
            },
            False
        ),
        (
            {
            "source": 'storage',
            "deliver_to": 'data_processor',
            "operation": 'return_historical_data'
            },
            True
        ),
        (
            {
            "source": 'storage',
            "deliver_to": 'data_processor',
            "operation": 'success_save'
            },
            False
        )
    ]
)
def test_check_operation(test_input, expected):
    assert check_operation(test_input) == expected