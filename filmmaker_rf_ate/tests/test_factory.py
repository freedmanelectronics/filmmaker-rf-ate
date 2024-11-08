from enum import Enum, auto

from functional_test_core.device_test import TestHandler, DeviceTest
from functional_test_core.device_test.observer import Message
from functional_test_core.mock import (
    MockDeviceTestTimerExecution,
    MockDeviceTestRaises,
    MockDeviceTestRetries,
)
from functional_test_core.models import DeviceInfo
from rode.devices.wireless.bases.wireless_device_base import WirelessDeviceBase

from filmmaker_rf_ate.config import Config
from filmmaker_rf_ate.tests.battery_test import BatteryTest
from filmmaker_rf_ate.tests.connection_stats_test import ConnectionStatsTest
from filmmaker_rf_ate.tests.firmware_version_test import FirmwareVersionTest
from filmmaker_rf_ate.tests.nvm_test import NvmTest
from filmmaker_rf_ate.tests.rf_power_test import RFPowerTest


def mock_test_factory(ref: DeviceInfo, dut: DeviceInfo) -> TestHandler:
    th = TestHandler(stop_on_fail=False, verbose=True)

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


def test_factory(ref: DeviceInfo, dut: DeviceInfo, config: Config, stop_on_fail:bool = True) -> TestHandler:
    tests = [
        FirmwareVersionTest(
            dut,
            config.tests.firmware.min_mcu_version,
            config.tests.firmware.min_nordic_version,
        ),
        # NvmTest(
        #     dut,
        #     config.tests.nvm.address,
        #     config.tests.nvm.expected_values,
        # ),
        ConnectionStatsTest(
            dut,
            ref,
            config.gender,
            config.tests.connection_stats.duration_short,
            config.tests.connection_stats.duration_long,
            config.tests.connection_stats.min_rssi,
            config.tests.connection_stats.allowed_errors,
        ),
        RFPowerTest(
            dut,
            config.arduino_com_port,
            config.tests.rf_power.channels,
            config.tests.rf_power.antennae,
        ),
        BatteryTest(dut),
    ]

    th = TestHandler(verbose=False, tests=tests, stop_on_fail=stop_on_fail)

    return th


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG
    from filmmaker_rf_ate.utils.get_devices import get_devices
    from functional_test_core.models.utils import spprint_devices

    ref, dut, _, _, _ = get_devices(
        CONFIG.device_classes.dut, CONFIG.device_classes.ref, hid_index=CONFIG.hid_index
    )

    th = test_factory(ref, dut, CONFIG)

    results = th.execute_tests()
    print(spprint_devices(dut))
