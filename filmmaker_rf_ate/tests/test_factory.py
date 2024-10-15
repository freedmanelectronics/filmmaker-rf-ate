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
from filmmaker_rf_ate.tests.connection_stats_test import ConnectionStatsTest
from filmmaker_rf_ate.tests.firmware_version_test import FirmwareVersionTest
from filmmaker_rf_ate.tests.nvm_test import NvmTest
from filmmaker_rf_ate.tests.rf_power_test import RFPowerTest


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


class FilmmakerTests(Enum):
    FIRMWARE: auto()
    NVM: auto()
    CONNECTION_STATS: auto()
    RF_POWER: auto()


class FilmmakerTestHandler(TestHandler):
    def __init__(self, config: Config, dut: DeviceInfo, ref: DeviceInfo):
        super().__init__(stop_on_fail=True, short_msg=True)
        self._config = config
        self._ref = ref
        self._dut = dut

        self._tests = {
            FilmmakerTests.FIRMWARE: FirmwareVersionTest(
                self._dut,
                self._config.tests.firmware.min_mcu_version,
                self._config.tests.firmware.min_nordic_version,
            ),
            FilmmakerTests.NVM: NvmTest(
                self._dut,
                self._config.tests.nvm.address,
                self._config.tests.nvm.expected_values,
            ),
            FilmmakerTests.CONNECTION_STATS: ConnectionStatsTest(
                self._dut,
                ref,
                self._config.gender,
                self._config.tests.connection_stats.duration_short,
                self._config.tests.connection_stats.duration_long,
                self._config.tests.connection_stats.min_rssi,
                self._config.tests.connection_stats.allowed_errors,
            ),
            FilmmakerTests.RF_POWER: RFPowerTest(
                self._dut,
                self._config.arduino_com_port,
                self._config.tests.rf_power.channels,
                self._config.tests.rf_power.antennae,
            ),
        }

        for test in self._tests.values():
            test.add_observer(self)

    @TestHandler.tests.setter
    def tests(self, value):
        raise NotImplementedError
