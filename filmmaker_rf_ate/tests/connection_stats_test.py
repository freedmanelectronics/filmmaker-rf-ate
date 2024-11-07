import time
from typing import Literal

from functional_test_core.device_test import DeviceTest
from functional_test_core.models import DeviceInfo, TestInfo
from rode.devices.wireless.commands.app_commands import AppCommands
from rode.devices.wireless.commands.radio_commands import RadioCommands


class ConnectionStatsTest(DeviceTest):
    def __init__(
        self,
        wireless: DeviceInfo,
        reference: DeviceInfo,
        gender: Literal["rx", "tx"],
        duration_short: int = 120,
        duration_long: int = 500,
        min_rssi: int = -95,
        allowed_errors: int = 1000,
    ):
        super().__init__("connection_stats", wireless, error_code="C")
        self._dut = wireless
        self._reference = reference
        self._gender = gender
        self._duration_short = duration_short
        self._duration_long = duration_long
        self._min_rssi = min_rssi
        self._allowed_errors = allowed_errors

        if self._gender == "tx":
            self._dut_rfid_idx = 1  # Pairs to RX
            self._ref_rfid_idx = 1  # Pairs to TX1
        elif self._gender == "rx":
            self._dut_rfid_idx = 1  # Pairs to TX1
            self._ref_rfid_idx = 1  # Pairs to RX
        else:
            raise ValueError(
                f"Unexpected gender `{self._gender}`, expected `rx` or `tx`"
            )

    def pre_test_routine(self) -> None:
        self._dut.rode_device.handle_command(AppCommands.set_system_state(True))
        self._reference.rode_device.handle_command(AppCommands.set_system_state(True))

        time.sleep(1)

        assert self._dut.rode_device.handle_command(
            AppCommands.system_is_on()
        ), "DUT could not be powered on"
        assert self._reference.rode_device.handle_command(
            AppCommands.system_is_on()
        ), "Reference could not be powered on"

    def test_routine(self) -> list[TestInfo]:
        ret = []

        dut_rfid = self._dut.rode_device.handle_command(RadioCommands.radio_get_rfid(0))
        ref_rfid = self._reference.rode_device.handle_command(
            RadioCommands.radio_get_rfid(0)
        )

        # exchange RFIDs
        self._dut.rode_device.handle_command(
            RadioCommands.radio_set_rfid(self._dut_rfid_idx, ref_rfid)
        )
        self._reference.rode_device.handle_command(
            RadioCommands.radio_set_rfid(self._ref_rfid_idx, dut_rfid)
        )
        time.sleep(2)

        # Verify that RFIDs have been exchanged
        dut_pair_rfid = self._dut.rode_device.handle_command(
            RadioCommands.radio_get_rfid(self._dut_rfid_idx)
        )
        wireless_passed = dut_pair_rfid == ref_rfid
        info = {"found_rfid": dut_pair_rfid, "expected_rfid": ref_rfid}
        ret.append(TestInfo("dut_paired", wireless_passed, info=info))

        ref_pair_rfid = self._reference.rode_device.handle_command(
            RadioCommands.radio_get_rfid(self._ref_rfid_idx)
        )
        ref_passed = ref_pair_rfid == dut_rfid
        info = {"found_rfid": ref_pair_rfid, "expected_rfid": dut_rfid}
        ret.append(TestInfo("ref_paired", ref_passed, info=info))

        if not (wireless_passed and ref_passed):
            return ret

        # Check min RSSI on short duration
        conn_stats_short = self._dut.rode_device.handle_command(
            RadioCommands.radio_get_advanced_connection_stats(0, self._duration_short)
        )

        conn_stats_retrieved = conn_stats_short is not None
        ret.append(TestInfo("connection_stats_short_measured", conn_stats_retrieved))

        if not conn_stats_retrieved:
            return ret


        rssi_passed = conn_stats_short.ch1_stats.avg_rssi >= self._min_rssi
        info = {
            "measured_average": conn_stats_short.ch1_stats.avg_rssi,
            "limits": {"min": self._min_rssi},
        }
        ret.append(TestInfo("min_rssi", rssi_passed, info=info))

        # Check total number of errors on long duration
        # conn_stats_long = self._dut.rode_device.handle_command(
        #     RadioCommands.radio_get_advanced_connection_stats(0, self._duration_long)
        # )
        #
        # conn_stats_retrieved = conn_stats_long is not None
        # ret.append(TestInfo("connection_stats_long_measured", conn_stats_retrieved))
        #
        # ch1_total_errors = (
        #     conn_stats_long.ch1_stats.audio_missed_errors
        #     + conn_stats_long.ch1_stats.audio_crc_errors
        #     + conn_stats_long.ch1_stats.beacon_errors
        # )
        # passed = ch1_total_errors < self._allowed_errors
        # info = {"total": ch1_total_errors, "allowed": self._allowed_errors}
        # ret.append(TestInfo("ch1_total_errors", passed, info=info))
        #
        # ch2_total_errors = (
        #     conn_stats_long.ch1_stats.audio_missed_errors
        #     + conn_stats_long.ch1_stats.audio_crc_errors
        #     + conn_stats_long.ch1_stats.beacon_errors
        # )
        # passed = ch2_total_errors < self._allowed_errors
        # info = {"total": ch2_total_errors, "allowed": self._allowed_errors}
        # ret.append(TestInfo("ch2_total_errors", passed, info=info))

        return ret

    def post_test_routine(self) -> None:
        # Reset RFID
        self._dut.rode_device.handle_command(
            RadioCommands.radio_set_rfid(self._dut_rfid_idx, bytes(0x0))
        )
        rfid = self._dut.rode_device.handle_command(
            RadioCommands.radio_get_rfid(self._dut_rfid_idx)
        )
        assert rfid == bytes([0, 0, 0, 0]), "Failed to reset DUT's paired RFID to zero."


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG
    from filmmaker_rf_ate.utils.get_devices import get_devices
    from functional_test_core.models.utils import spprint_devices

    ref, dut1, _, _, _ = get_devices(
        CONFIG.device_classes.dut, CONFIG.device_classes.ref
    )

    test = ConnectionStatsTest(
        dut1,
        ref,
        CONFIG.gender,
        CONFIG.tests.connection_stats.duration_short,
        CONFIG.tests.connection_stats.duration_long,
        CONFIG.tests.connection_stats.min_rssi,
        CONFIG.tests.connection_stats.allowed_errors,
    )
    result = test.execute_test()

    print(spprint_devices(dut1))
