# Tests firmware version
from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, FailureMode
from rode.devices.wireless.commands.app_commands import AppCommands
from rode.devices.common.commands.basic_commands import CommonCommands
from pkg_resources import packaging

from filmmaker_rf_ate.utils import get_devices


class FirmwareVersionTest(DeviceTest):
    def __init__(
        self, wireless: DeviceInfo, min_firmware_version: str, min_nordic_version: str
    ):
        super().__init__("nvm_test", [wireless])
        self.__wireless = wireless
        self.__min_firmware_version = min_firmware_version
        self.__min_nordic_verison = min_nordic_version

    def test_routine(self) -> list[FailureMode]:
        ret = []

        firmware_version = self.__wireless.rode_device.handle_command(
            CommonCommands.app_version()
        )
        passed = packaging.version.parse(
            str(firmware_version)[2:]
        ) >= packaging.version.parse(self.__min_firmware_version)
        info = {"found": str(firmware_version), "minimum": self.__min_firmware_version}
        ret.append(FailureMode("firmware_version", passed, info=info))

        nordic_version = self.__wireless.rode_device.handle_command(
            AppCommands.radio_version()
        )
        passed = packaging.version.parse(
            str(nordic_version)[2:]
        ) >= packaging.version.parse(self.__min_nordic_verison)
        info = {"found": str(nordic_version), "minimum": self.__min_nordic_verison}
        ret.append(FailureMode("nordic_version", passed, info=info))

        return ret


if __name__ == "__main__":
    reference, rxs = get_devices()

    test = FirmwareVersionTest(rxs[0], "0.12", "2.05")
    result = test.execute_test()

    print(result)
