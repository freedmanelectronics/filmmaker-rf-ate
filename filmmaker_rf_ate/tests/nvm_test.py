# Tests non volatile memory
from typing import Literal

from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, FailureMode
from rode.devices.wireless.commands.nvm_commands import NVMReadCommand

from filmmaker_rf_ate.utils import get_devices


class NvmTest(DeviceTest):
    def __init__(self, wireless: DeviceInfo, gender: Literal["rx", "tx"]):
        super().__init__("nvm_test", [wireless])
        self.__wireless = wireless

        if gender == "rx":
            self.__exp_nvm_values = bytes([0x00, 0x00, 0x04, 0x01])
        elif gender == "tx":
            self.__exp_nvm_values = bytes([0x00, 0x04, 0x01, 0x00])
        else:
            raise ValueError(
                f"Unexpected gender value `{gender}` - expected `rx` or `tx`"
            )

    def test_routine(self) -> list[FailureMode]:
        nvm = self.__wireless.rode_device.handle_command(NVMReadCommand(0x08, 4))

        passed = nvm == self.__exp_nvm_values
        info = {"read": nvm, "expected": self.__exp_nvm_values}

        return [FailureMode("nvm_value", passed, info=info)]


if __name__ == "__main__":
    reference, rxs = get_devices()

    test = NvmTest(rxs[0], "tx")
    result = test.execute_test()

    print(result)
