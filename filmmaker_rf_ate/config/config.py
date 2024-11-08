from os import PathLike
from pathlib import Path
from typing import Literal

import yaml

from rode.devices.wireless.wireless_go_2_rx import WirelessGo2Rx
from rode.devices.wireless.wireless_go_2_tx import WirelessGo2Tx
from rode.devices.wireless.wireless_go_3_tx import WirelessGo3Tx
from rode.devices.wireless.wireless_go_3_rx import WirelessGo3Rx

# from rode.devices.wireless.filmmaker_2_rx import Filmmaker2Rx
# from rode.devices.wireless.filmmaker_2_tx import Filmmaker2Tx
from rode.devices.wireless.bases.wireless_device_base import WirelessDeviceBase
from dataclasses import dataclass, field

from filmmaker_rf_ate.config.tests import TestConfig

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
