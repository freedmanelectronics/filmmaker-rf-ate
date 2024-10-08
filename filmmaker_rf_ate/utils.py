from functional_test_core.utils import get_connected_devices
from filmmaker_rf_ate.config import CONFIG


def get_devices():
    """
    Gets connected WiGo3 devices. Throws an assertion error if an unexpected number of devices are connected.

    @return: Device info of charging case, WiGo3 RX, and two WiGo3 TXs respectively.
    """
    devices = get_connected_devices()
    references = [
        device
        for device in devices
        if isinstance(device.rode_device, CONFIG.device_classes.ref)
    ]
    duts = [
        device
        for device in devices
        if isinstance(device.rode_device, CONFIG.device_classes.dut)
    ]

    return references[0], duts
