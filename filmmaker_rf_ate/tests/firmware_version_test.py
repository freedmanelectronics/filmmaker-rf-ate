# Tests firmware version
from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, FailureMode
from rode.devices.wireless.commands.app_commands import AppCommands
from rode.devices.common.commands.basic_commands import CommonCommands
from rode.devices.utils.versions import Version

from filmmaker_rf_ate.utils import get_devices


class FirmwareVersionTest(DeviceTest):
    def __init__(
        self,
        wireless: DeviceInfo,
        min_firmware_version: Version,
        min_nordic_version: Version,
    ):
        super().__init__("firmware_version", [wireless])
        self._wireless = wireless
        self._min_firmware_version = min_firmware_version
        self._min_nordic_verison = min_nordic_version

    def test_routine(self) -> list[FailureMode]:
        ret = []

        firmware_version = self._wireless.rode_device.handle_command(
            CommonCommands.app_version()
        )
        passed = firmware_version >= self._min_firmware_version
        info = {
            "found": str(firmware_version),
            "minimum": str(self._min_firmware_version),
        }
        ret.append(FailureMode("firmware_version", passed, info=info))

        nordic_version = self._wireless.rode_device.handle_command(
            AppCommands.radio_version()
        )
        passed = nordic_version >= self._min_nordic_verison
        info = {"found": str(nordic_version), "minimum": str(self._min_nordic_verison)}
        ret.append(FailureMode("nordic_version", passed, info=info))

        return ret


if __name__ == "__main__":
    reference, duts = get_devices()

    test = FirmwareVersionTest(duts[0], Version("0.1.2"), Version("0.2.5"))
    result = test.execute_test()

    print(result)
    print(result.failure_modes[2])
