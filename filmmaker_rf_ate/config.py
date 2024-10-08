from os import PathLike
from pathlib import Path
from typing import Literal

import yaml
from rode.devices.wireless.wireless_go_2_rx import WirelessGo2Rx
from rode.devices.wireless.wireless_go_2_tx import WirelessGo2Tx
from rode.devices.wireless.wireless_go_3_tx import WirelessGo3Tx
from rode.devices.wireless.wireless_go_3_rx import WirelessGo3Rx
from rode.devices.wireless.bases.wireless_device_base import WirelessDeviceBase
from dataclasses import dataclass


DEFAULT_CONFIG_PATH = Path.cwd() / "config.yaml"
REF_RX_CLASS = WirelessGo2Rx
REF_TX_CLASS = WirelessGo2Tx
RX_CLASS = WirelessGo3Rx
TX_CLASS = WirelessGo3Tx


@dataclass
class DeviceClasses:
    dut: type(WirelessDeviceBase)
    ref: type(WirelessDeviceBase)


@dataclass
class Config:
    dut_type: Literal["rx", "tx"]
    device_classes: DeviceClasses = None

    def __post_init__(self):
        if self.dut_type == "rx":
            self.device_classes = DeviceClasses(RX_CLASS, REF_TX_CLASS)
        elif self.dut_type == "tx":
            self.device_classes = DeviceClasses(TX_CLASS, REF_RX_CLASS)
        else:
            raise ValueError(f"Unknown DUT type `{self.dut_type}`")


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
