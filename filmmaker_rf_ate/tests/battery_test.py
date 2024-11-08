# Tests battery
from datetime import datetime, timedelta

from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, TestInfo
from rode.devices.wireless.commands.app_commands import GetFuelGaugeCommand, FuelGaugeData


class BatteryTest(DeviceTest):
    def __init__(
        self,
        wireless: DeviceInfo,
        initial_measurement_time: datetime | None = None,
        initial_battery_info: FuelGaugeData | None = None
    ):
        super().__init__("battery", wireless, error_code="B")
        self._wireless = wireless
        self._initial_timestamp = datetime.now() if initial_measurement_time is None else initial_measurement_time
        self._initial_battery_info = self._wireless.rode_device.handle_command(
            GetFuelGaugeCommand()
        ) if initial_battery_info is None else initial_battery_info

    def test_routine(self) -> list[TestInfo]:
        time_since_measurement = datetime.now() - self._initial_timestamp
        self.notify_observers(
            self._create_message(
                "running",
                f"Battery percentage was {self._initial_battery_info.battery_soc}, measured {time_since_measurement.total_seconds()}s ago",
            ),
        )

        battery_info = self._wireless.rode_device.handle_command(GetFuelGaugeCommand())
        passed = (
            battery_info.battery_soc > self._initial_battery_info.battery_soc
            or battery_info.battery_soc == 100
        )
        info = {
            "initial_percentage": self._initial_battery_info.battery_soc,
            "seconds_since_measurement": time_since_measurement.total_seconds(),
            "percentage": battery_info.battery_soc,
            "voltage": battery_info.battery_voltage,
            "temperature": battery_info.battery_temp,
        }

        if passed:
            self.notify_observers(
                self._create_message(
                    "pass",
                    "Battery test passed!",
                ),
            )
        else:
            self.notify_observers(
                self._create_message(
                    "fail",
                    f"Battery test failed! Measured {battery_info.battery_soc}, was {self._initial_battery_info.battery_soc} {time_since_measurement.total_seconds()}s ago.",
                ),
            )

        return [TestInfo("battery_stats", passed, info=info)]


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

    initial_time = datetime.now() - timedelta(hours=1)
    test = BatteryTest(dut)
    results = test.execute_test()

    print(spprint_devices(dut))
