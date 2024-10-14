from functional_test_core.device_test import TestHandler
from functional_test_core.device_test.observer import Message
from functional_test_core.mock import (
    MockDeviceTestTimerExecution,
    MockDeviceTestRaises,
    MockDeviceTestRetries,
)
from functional_test_core.models import DeviceInfo

from filmmaker_rf_ate.config import Config


def test_factory(
    ref: DeviceInfo, dut: DeviceInfo
) -> TestHandler:
    """
    Factory method for generating tests

    @param gui_observer: gui observer object
    @param product_family: product family
    @param charge_case_type: type of charge case
    @param mock:
    @param config:
    @return:
    """
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
