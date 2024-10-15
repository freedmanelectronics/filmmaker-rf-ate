from functional_test_core.device_test import TestHandler
from functional_test_core.device_test.observer import Message
from functional_test_core.mock import (
    MockDeviceTestTimerExecution,
    MockDeviceTestRaises,
    MockDeviceTestRetries,
)
from functional_test_core.models import DeviceInfo

from filmmaker_rf_ate.config import Config


def mock_test_factory(ref: DeviceInfo, dut: DeviceInfo) -> TestHandler:
    th = TestHandler(stop_on_fail=False, short_msg=True)

    kwargs = {
        "execution_duration": 1,
        "pre_test_duration": 1,
        "post_test_duration": 1,
    }
    th.tests = [
        MockDeviceTestTimerExecution([ref, dut], **kwargs),
        MockDeviceTestRetries([ref, dut], 5, succeed_on_try=4),
        MockDeviceTestTimerExecution([ref, dut], **kwargs),
        MockDeviceTestRaises([ref, dut]),
        MockDeviceTestTimerExecution([ref, dut], **kwargs),
    ]

    return th


class FilmmakerTestHandler(TestHandler):
    def __init__(self):
        super().__init__(stop_on_fail=True, short_msg=True)
