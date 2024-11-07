# Tests non volatile memory
from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, TestInfo
from rode.devices.wireless.commands.nvm_commands import NVMReadCommand


class NvmTest(DeviceTest):
    def __init__(self, wireless: DeviceInfo, address: int, expected_values: bytes):
        super().__init__("nvm_test", wireless, error_code="N")
        self._wireless = wireless
        self._nvm_address = address
        self._exp_nvm_values = expected_values

    def test_routine(self) -> list[TestInfo]:
        nvm = self._wireless.rode_device.handle_command(
            NVMReadCommand(self._nvm_address, len(self._exp_nvm_values))
        )

        passed = nvm == self._exp_nvm_values
        info = {"read": nvm, "expected": self._exp_nvm_values}

        return [TestInfo("nvm_value", passed, info=info)]


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG
    from filmmaker_rf_ate.utils.get_devices import get_devices
    from functional_test_core.models.utils import spprint_devices

    reference, dut, _, _, _ = get_devices(
        CONFIG.device_classes.dut, CONFIG.device_classes.ref, hid_index=CONFIG.hid_index
    )

    test = NvmTest(dut, CONFIG.tests.nvm.address, CONFIG.tests.nvm.expected_values)
    result = test.execute_test()

    print(spprint_devices(dut))
