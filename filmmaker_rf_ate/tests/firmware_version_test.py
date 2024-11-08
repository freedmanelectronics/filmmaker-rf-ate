# Tests firmware version
from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, TestInfo
from rode.devices.wireless.commands.app_commands import AppCommands
from rode.devices.common.commands.basic_commands import CommonCommands
from rode.devices.utils.versions import Version


class FirmwareVersionTest(DeviceTest):
    def __init__(
        self,
        wireless: DeviceInfo,
        min_firmware_version: Version,
        min_nordic_version: Version,
    ):
        super().__init__("firmware_version", wireless, error_code="F")
        self._wireless = wireless
        self._min_firmware_version = min_firmware_version
        self._min_nordic_version = min_nordic_version

        self._test_params = {
            "min_firmware_version": str(self._min_firmware_version),
            "min_nordic_version": str(self._min_nordic_version),
        }

    def test_routine(self) -> list[TestInfo]:
        ret = []

        firmware_version = self._wireless.rode_device.handle_command(
            CommonCommands.app_version()
        )
        passed = firmware_version.version >= self._min_firmware_version
        info = {
            "found": str(firmware_version),
            "minimum": str(self._min_firmware_version),
        }
        ret.append(TestInfo("firmware_version", passed, info=info))

        if passed:
            self.notify_observers(
                self._create_message(
                    "pass",
                    f"Firmware passed! Found {str(firmware_version)}",
                ),
            )
        else:
            self.notify_observers(
                self._create_message(
                    "fail",
                    f"Firmware failed. Found {str(firmware_version)}, expected >{str(self._min_firmware_version)}",
                ),
            )

        nordic_version = self._wireless.rode_device.handle_command(
            AppCommands.radio_version()
        )
        passed = nordic_version.version >= self._min_nordic_version
        info = {"found": str(nordic_version), "minimum": str(self._min_nordic_version)}
        ret.append(TestInfo("nordic_version", passed, info=info))

        if passed:
            self.notify_observers(
                self._create_message(
                    "pass",
                    f"Nordic version passed! Found {str(nordic_version)}",
                ),
            )
        else:
            self.notify_observers(
                self._create_message(
                    "fail",
                    f"Nordic version failed. Found {str(nordic_version)}, expected >{str(self._min_nordic_version)}",
                ),
            )

        return ret


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG
    from filmmaker_rf_ate.utils.get_devices import get_devices
    from functional_test_core.models.utils import spprint_devices
    import logging

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    reference, dut, _, _, _ = get_devices(
        CONFIG.device_classes.dut, CONFIG.device_classes.ref, hid_index=CONFIG.hid_index
    )

    test = FirmwareVersionTest(
        dut,
        CONFIG.tests.firmware.min_mcu_version,
        CONFIG.tests.firmware.min_nordic_version,
    )
    result = test.execute_test()

    print(spprint_devices(dut))
