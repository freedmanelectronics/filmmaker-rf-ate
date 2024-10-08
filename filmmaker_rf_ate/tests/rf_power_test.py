import time
from statistics import mean
from functional_test_core.device_test import DeviceTest
from functional_test_core.device_test.device_test import DeviceTestTeardownException
from functional_test_core.device_test.observer import Message
from functional_test_core.models import DeviceInfo, FailureMode
from rode.devices.wireless.commands.app_commands import AppCommands
from rode.devices.wireless.commands.radio_commands import (
    RadioCommands,
    RadioAntennaIndex,
)
from rode.devices.wireless.commands.radio_channels import RadioChannel
from rode.devices.common.commands.basic_commands import CommonCommands

from filmmaker_rf_ate.arduino.arduino import RFATEArduino
from filmmaker_rf_ate.utils import get_devices


class TestSetupException(Exception):
    pass


class RFPowerTest(DeviceTest):
    _antennae = [RadioAntennaIndex.ANTENNA_1, RadioAntennaIndex.ANTENNA_2]

    def __init__(
        self,
        wireless: DeviceInfo,
        com_port: str,
        channels: list[RadioChannel] = None,
        antennae_min_delta: dict[RadioAntennaIndex, float] = None,
    ):
        super().__init__("connection_stats", [wireless])
        self._dut = wireless
        self._com_port = com_port
        self._channels = (
            [
                RadioChannel.CHANNEL_0,
                RadioChannel.CHANNEL_20,
                RadioChannel.CHANNEL_40,
                RadioChannel.CHANNEL_60,
                RadioChannel.CHANNEL_80,
            ]
            if not channels
            else channels
        )
        self._antennae_min_delta = (
            {RadioAntennaIndex.ANTENNA_1: 5.0, RadioAntennaIndex.ANTENNA_2: 5.0}
            if not antennae_min_delta
            else antennae_min_delta
        )

    def pre_test_routine(self) -> None:
        self._dut.rode_device.handle_command(AppCommands.set_system_state(True))
        exc = None
        for i in range(5):
            try:
                assert self._dut.rode_device.handle_command(
                    AppCommands.system_is_on()
                ), "DUT could not be powered on"
                return
            except (AssertionError, OSError) as e:
                exc = e
                time.sleep(0.1)

        raise (
            exc
            if exc
            else TestSetupException("Could not power on device, retries exceeded")
        )

    def test_routine(self) -> list[FailureMode]:
        ret = []

        with RFATEArduino(self._com_port) as ard:
            ard.set_mode("M")

            info = {}
            for antenna, min_delta in self._antennae_min_delta.items():
                high_power_results = []
                low_power_results = []
                delta_power_results = []

                antenna_info = {}

                for channel in self._channels:
                    self.notify_observers(
                        Message(
                            "running",
                            self.name,
                            f"Testing power high on antennae {antenna} @ channel {channel}",
                        )
                    )
                    self._dut.rode_device.handle_command(
                        RadioCommands.radio_start_continuous_wave_test_mode_fixedfreq(
                            channel, antenna, 0x04
                        )
                    )
                    pow_high = ard.get_radio_power()
                    high_power_results.append(pow_high)
                    self.notify_observers(
                        Message(
                            "running",
                            self.name,
                            f"Antenna {antenna} power high measured at {pow_high} dBm",
                        )
                    )
                    time.sleep(0.3)  # very important delay, has to be 0.3s , not 1.0s

                    self.notify_observers(
                        Message(
                            "running",
                            self.name,
                            f"Testing power low on antennae {antenna} @ channel {channel}",
                        )
                    )
                    self._dut.rode_device.handle_command(
                        RadioCommands.radio_start_continuous_wave_test_mode_fixedfreq(
                            channel, antenna, 0xEC
                        )
                    )
                    pow_low = ard.get_radio_power()
                    low_power_results.append(pow_low)
                    time.sleep(0.3)  # very important delay, has to be 0.3s , not 1.0s

                    delta_pow = abs(pow_high - pow_low)
                    delta_power_results.append(delta_pow)
                    self.notify_observers(
                        Message(
                            "running",
                            self.name,
                            f"Antenna {antenna} power delta measured at {delta_pow} dBm",
                        )
                    )
                    antenna_info[channel.name] = {
                        "power_high": pow_high,
                        "power_low": pow_low,
                        "pow_delta": delta_pow,
                    }

                avg_pow = mean(delta_power_results)
                passed = avg_pow > min_delta
                info = {
                    "channels": antenna_info,
                    "limits": {"delta_power": {"min": min_delta}},
                    "mean_delta_power": avg_pow,
                }
                ret.append(FailureMode(f"{antenna.name}_avg_power", passed, info=info))

            ard.set_mode("P")

        return ret

    def post_test_routine(self) -> None:
        self._dut.rode_device.handle_command(
            RadioCommands.radio_start_continuous_receive_test_mode(
                RadioChannel.CHANNEL_0, RadioAntennaIndex.ANTENNA_1
            )
        )
        self._dut.rode_device.handle_command(
            RadioCommands.radio_start_continuous_receive_test_mode(
                RadioChannel.CHANNEL_0, RadioAntennaIndex.ANTENNA_2
            )
        )
        self._dut.rode_device.handle_command(CommonCommands.reset())

        # Confirm device rebooted
        exc = None
        for i in range(15):
            try:
                self._dut.rode_device.handle_command(CommonCommands.app_version())
                return
            except OSError as e:
                exc = e
                time.sleep(0.5)

        raise exc if exc else DeviceTestTeardownException()


if __name__ == "__main__":
    ref, duts = get_devices()

    test = RFPowerTest(duts[0], "COM4")
    result = test.execute_test()

    print(result)

    for fm in result.failure_modes:
        print(fm)
