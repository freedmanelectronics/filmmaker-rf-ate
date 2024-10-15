from os import PathLike
from pathlib import Path
from typing import Literal

import yaml
from rode.devices.utils.versions import Version
from rode.devices.wireless.commands.radio_channels import RadioChannel
from rode.devices.wireless.commands.radio_commands import RadioAntennaIndex
from rode.devices.wireless.wireless_go_2_rx import WirelessGo2Rx
from rode.devices.wireless.wireless_go_2_tx import WirelessGo2Tx
from rode.devices.wireless.wireless_go_3_tx import WirelessGo3Tx
from rode.devices.wireless.wireless_go_3_rx import WirelessGo3Rx

# from rode.devices.wireless.filmmaker_2_rx import Filmmaker2Rx
# from rode.devices.wireless.filmmaker_2_tx import Filmmaker2Tx
from rode.devices.wireless.bases.wireless_device_base import WirelessDeviceBase
from dataclasses import dataclass, field

DEFAULT_CONFIG_PATH = Path.cwd() / "config.yaml"
REF_RX_CLASS = WirelessGo2Rx
REF_TX_CLASS = WirelessGo2Tx
RX_CLASS = WirelessGo3Rx  # Filmmaker2Rx
TX_CLASS = WirelessGo3Tx  # Filmmaker2Tx


@dataclass
class DeviceClasses:
    dut: type(WirelessDeviceBase)
    ref: type(WirelessDeviceBase)


@dataclass
class FirmwareTestConfig:
    min_mcu_version: Version = field(default_factory=lambda: Version("0.1.2"))
    min_nordic_version: Version = field(default_factory=lambda: Version("0.2.5"))

    def __post_init__(self):
        if isinstance(self.min_mcu_version, str):
            self.min_mcu_version = Version(self.min_mcu_version)

        if isinstance(self.min_nordic_version, str):
            self.min_nordic_version_version = Version(self.min_nordic_version)


@dataclass
class NvmTestConfig:
    address: int
    expected_values: bytes

    def __init__(self, gender: Literal["rx", "tx"]):
        if gender == "rx":
            self.address = 0xC
            self.expected_values = b"\x00\x00\x04\x01"
        elif gender == "tx":
            self.address = 0x8
            self.expected_values = b"\x00\x04\x01\x00"
        else:
            raise ValueError(f"Unknown DUT gender `{gender}`")


@dataclass
class ConnectionStatsTestConfig:
    duration_short: int = 120
    duration_long: int = 500
    min_rssi: int = -95
    allowed_errors: int = 1000


@dataclass
class AntennaConfig:
    antenna: RadioAntennaIndex
    min_delta: float = 5.0

    def __post_init__(self):
        self.antenna = (
            RadioAntennaIndex[self.antenna]
            if isinstance(self.antenna, str)
            else RadioAntennaIndex(self.antenna)
        )


@dataclass
class RfPowerTestConfig:
    channels: list[RadioChannel] = field(
        default_factory=lambda: [
            RadioChannel.CHANNEL_0,
            RadioChannel.CHANNEL_20,
            RadioChannel.CHANNEL_40,
            RadioChannel.CHANNEL_60,
            RadioChannel.CHANNEL_80,
        ]
    )
    antennae: list[AntennaConfig] = field(
        default_factory=lambda: [
            AntennaConfig(RadioAntennaIndex.ANTENNA_1, 5.0),
            AntennaConfig(RadioAntennaIndex.ANTENNA_2, 5.0),
        ]
    )

    def __post_init__(self):
        self.channels = [
            RadioChannel[channel] if isinstance(channel, str) else RadioChannel(channel)
            for channel in self.channels
        ]

        antennae = []

        for antenna in self.antennae:
            if isinstance(antenna, dict):
                antenna = AntennaConfig(**antenna)
            antennae.append(antenna)

        self.antennae = antennae


@dataclass
class TestConfig:
    gender: Literal["rx", "tx"]
    nvm: NvmTestConfig = None
    firmware: FirmwareTestConfig = field(default_factory=lambda: FirmwareTestConfig())
    connection_stats: ConnectionStatsTestConfig = field(
        default_factory=lambda: ConnectionStatsTestConfig()
    )
    rf_power: RfPowerTestConfig = field(default_factory=lambda: RfPowerTestConfig())

    def __post_init__(self):
        if isinstance(self.firmware, dict):
            self.firmware = FirmwareTestConfig(**self.firmware)

        if isinstance(self.rf_power, dict):
            self.rf_power = RfPowerTestConfig(**self.rf_power)

        self.nvm = NvmTestConfig(self.gender)


@dataclass
class Config:
    gender: Literal["rx", "tx"]
    arduino_com_port: str = "COM4"
    device_classes: DeviceClasses = None
    tests: TestConfig = None

    def __post_init__(self):
        if self.gender == "rx":
            self.device_classes = DeviceClasses(RX_CLASS, REF_TX_CLASS)
        elif self.gender == "tx":
            self.device_classes = DeviceClasses(TX_CLASS, REF_RX_CLASS)
        else:
            raise ValueError(f"Unknown DUT type `{self.gender}`")

        if isinstance(self.tests, dict):
            self.tests = TestConfig(self.gender, **self.tests)
        else:
            self.tests = TestConfig(self.gender)


def read_config(config_yaml_path: PathLike = None) -> Config:
    """
    Reads config
    @param config_yaml_path: path to config yaml file. If none, defaults to "config.yaml" in project root.
    @return: parsed config object
    """
    config_yaml_path = DEFAULT_CONFIG_PATH if not config_yaml_path else config_yaml_path

    with open(config_yaml_path) as file:
        yaml_str = file.read()
        parsed_yaml = yaml.safe_load(yaml_str)

    return Config(**parsed_yaml)


CONFIG = read_config()
