# Tests RFID assignment
from functional_test_core.device_test import DeviceTest
from functional_test_core.device_test.observer import Message
from functional_test_core.models import DeviceInfo, TestInfo
from rfid_server import RfidService
from rfid_server.remote_proxy.client import Client
from rode.devices.wireless.commands.radio_commands import RadioSetRfId, RadioGetRfId


class RfidAssignmentTest(DeviceTest):
    def __init__(self, wireless: DeviceInfo, rfid_client: Client, expected_first_byte_value: int = 8):
        super().__init__("nvm_test", [wireless], error_code="N")
        self._wireless = wireless
        self._rfid_client = rfid_client
        self._comment = "filmmaker_rf_ate"
        self._expected_first_byte_value = expected_first_byte_value

    def test_routine(self) -> list[TestInfo]:
        device_rfid = self._wireless.rode_device.handle_command(RadioGetRfId(0))

        if device_rfid == b'\xff\xff\xff\xff': # RFID has not been assigned
            rfid_from_server = self._rfid_client.next(
                self._wireless.product_family.name,
                self._wireless.product_family.product_id,
                comment=self._comment,
            )
            rfid_bytes = bytes.fromhex(rfid_from_server[2:])

            self.notify_observers(
                Message(
                    "running",
                    self.name,
                    f"Assigning device RFID {rfid_bytes}",
                )
            )
            self._wireless.rode_device.handle_command(RadioSetRfId(0, rfid_bytes))

            device_rfid = self._wireless.rode_device.handle_command(RadioGetRfId(0))

            passed = device_rfid == rfid_bytes
            info = {"device_rfid": device_rfid, "expected": rfid_bytes}

            ret = TestInfo("rfid_assigned", passed, info=info)
        else:
            # Check that first byte == 8
            passed = device_rfid[0] & 0xf0 == 0x080
            info = {"device_rfid": device_rfid}
            ret = TestInfo('rfid_valid', passed, info=info
                           )
        if passed:
            self.notify_observers(
                Message(
                    "pass",
                    self.name,
                    "RFID test successful.",
                )
            )
        else:
            self.notify_observers(
                Message(
                    "fail",
                    self.name,
                    "RFID test failed.",
                )
            )

        return [ret]


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG
    from filmmaker_rf_ate.utils.get_devices import get_devices

    reference, dut, _, _, _ = get_devices(
        CONFIG.device_classes.dut, CONFIG.device_classes.ref
    )

    client = Client(
        RfidService,
        CONFIG.tests.rfid_assignment.hostname,
        CONFIG.tests.rfid_assignment.port,
    )

    test = RfidAssignmentTest(dut, client)
    result = test.execute_test()

    print(result)
