# Tests battery
from datetime import datetime, timedelta

from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, TestInfo
from rode.devices.wireless.commands.app_commands import GetFuelGaugeCommand


class BatteryTest(DeviceTest):
    def __init__(
        self,
        wireless: DeviceInfo,
    ):
        super().__init__("battery", [wireless], error_code="B")
        self._wireless = wireless
        self._initial_timestamp = datetime.now()
        self._initial_battery_info = self._wireless.rode_device.handle_command(
            GetFuelGaugeCommand()
        )

    def test_routine(self) -> list[TestInfo]:
        battery_info = self._wireless.rode_device.handle_command(GetFuelGaugeCommand())

        time_since_measurement = datetime.now() - self._initial_timestamp
        passed = (
            battery_info.battery_soc > self._initial_battery_info.battery_soc
            or battery_info.battery_soc == 100
        )
        info = {
            "initial_percentage": self._initial_battery_info.battery_soc,
            "time_since_measurement": time_since_measurement.total_seconds(),
            "percentage": battery_info.battery_soc,
            "voltage": battery_info.battery_voltage,
            "temperature": battery_info.battery_temp,
        }

        return [TestInfo("battery_stats", passed, info=info)]


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG
    from filmmaker_rf_ate.get_devices import get_devices

    reference, dut, _, _, _ = get_devices(
        CONFIG.device_classes.dut, CONFIG.device_classes.ref
    )

    initial_time = datetime.now() - timedelta(hours=1)
    test = BatteryTest(dut)
    results = test.execute_test()

    print(results)
    print(results.failure_modes[1])
