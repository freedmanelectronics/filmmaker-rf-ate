# Tests non volatile memory
from typing import Literal

from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, FailureMode
from rode.devices.wireless.commands.nvm_commands import NVMReadCommand


class NvmTest(DeviceTest):
    def __init__(self, wireless: DeviceInfo, address: int, expected_values: bytes):
        super().__init__("nvm_test", [wireless])
        self._wireless = wireless
        self._nvm_address = address
        self._exp_nvm_values = expected_values

    def test_routine(self) -> list[FailureMode]:
        nvm = self._wireless.rode_device.handle_command(
            NVMReadCommand(self._nvm_address, len(self._exp_nvm_values))
        )

        passed = nvm == self._exp_nvm_values
        info = {"read": nvm, "expected": self._exp_nvm_values}

        return [FailureMode("nvm_value", passed, info=info)]


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG
    from filmmaker_rf_ate.get_devices import get_devices

    reference, dut, _, _, _ = get_devices(
        CONFIG.device_classes.dut, CONFIG.device_classes.ref
    )

    test = NvmTest(dut, CONFIG.tests.nvm.address, CONFIG.tests.nvm.expected_values)
    result = test.execute_test()

    print(result)
