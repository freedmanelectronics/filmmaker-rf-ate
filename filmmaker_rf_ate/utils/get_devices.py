import logging
import platform

from functional_test_core.models import DeviceInfo
from functional_test_core.utils import get_connected_devices, get_devices_by_hid
from requests import Session
from rode.core.device_base import RodeDeviceBase
from rode.devices.wireless.bases.wireless_device_base import WirelessDeviceBase


def _get_device_of_class(
    connected_devices: list[DeviceInfo], dut_class: type(RodeDeviceBase), index: int = 0
) -> DeviceInfo | None:
    duts = [
        device
        for device in connected_devices
        if isinstance(device.rode_device, dut_class)
    ]
    try:
        return duts[index]
    except IndexError:
        return None


def _get_devices_windows(
    dut_class: type(WirelessDeviceBase),
    ref_class: type(WirelessDeviceBase),
    session: Session = None,
) -> tuple[
    DeviceInfo | None,
    DeviceInfo | None,
    DeviceInfo | None,
    DeviceInfo | None,
    DeviceInfo | None,
]:
    connected_devices = get_connected_devices(session)

    refs = [
        device
        for device in connected_devices
        if isinstance(device.rode_device, ref_class)
    ]
    ref = refs[0] if 0 < len(refs) else None
    if ref:
        ref.name_short = "reference"

    duts = [
        device
        for device in connected_devices
        if isinstance(device.rode_device, dut_class)
    ]
    dut1 = duts[0] if 0 < len(duts) else None
    dut2 = duts[1] if 1 < len(duts) else None
    dut3 = duts[2] if 2 < len(duts) else None
    dut4 = duts[3] if 3 < len(duts) else None

    if dut1:
        dut1.name_short = "dut1"

    if dut2:
        dut2.name_short = "dut2"

    if dut3:
        dut3.name_short = "dut3"

    if dut4:
        dut4.name_short = "dut4"

    return ref, dut1, dut2, dut3, dut4


def _get_devices_linux(
    dut_class, ref_class, session: Session = None
) -> tuple[
    DeviceInfo | None,
    DeviceInfo | None,
    DeviceInfo | None,
    DeviceInfo | None,
    DeviceInfo | None,
]:
    devices = get_devices_by_hid([dut_class, ref_class], session)

    ref = next(iter(devices[ref_class].values()), None)

    dut1_path = next(
        iter(
            [
                hid_path
                for hid_path in devices[dut_class].keys()
                if hid_path[8] == b"4"[0]
            ]
        ),
        None,
    )
    dut2_path = next(
        iter(
            [
                hid_path
                for hid_path in devices[dut_class].keys()
                if hid_path[8] == b"3"[0]
            ]
        ),
        None,
    )
    dut3_path = next(
        iter(
            [
                hid_path
                for hid_path in devices[dut_class].keys()
                if hid_path[8] == b"2"[0]
            ]
        ),
        None,
    )
    dut4_path = next(
        iter(
            [
                hid_path
                for hid_path in devices[dut_class].keys()
                if hid_path[8] == b"1"[0]
            ]
        ),
        None,
    )

    dut1 = devices[dut_class].get(dut1_path)
    dut2 = devices[dut_class].get(dut2_path)
    dut3 = devices[dut_class].get(dut3_path)
    dut4 = devices[dut_class].get(dut4_path)

    return ref, dut1, dut2, dut3, dut4


def get_devices(
    dut_class: type(WirelessDeviceBase),
    ref_class: type(WirelessDeviceBase),
    session: Session = None,
    retries: int = 0,
    delay: float = 0.1,
) -> tuple[DeviceInfo, DeviceInfo, DeviceInfo, DeviceInfo, DeviceInfo]:
    """
    Gets connected WiGo3 devices. Throws an assertion error if an unexpected number of devices are connected.

    @return: Device info of charging case, WiGo3 RX, and two WiGo3 TXs respectively.
    """

    operating_system = platform.system()
    logger = logging.getLogger("get_devices")
    ref, dut1, dut2, dut3, dut4 = None, None, None, None, None
    for i in range(retries + 1):
        if operating_system == "Linux":
            ref, dut1, dut2, dut3, dut4 = _get_devices_linux(
                dut_class, ref_class, session=session
            )
        elif operating_system == "Windows":
            logger.warning(
                "get_devices cannot index devices to physical ports. It is recommended to manually check rejects, "
                "or to test one DUT at a time."
            )
            ref, dut1, dut2, dut3, dut4 = _get_devices_windows(
                dut_class, ref_class, session=session
            )
        else:
            raise NotImplementedError(f"OS `{operating_system}` not supported")

        if all([ref, dut1, dut2, dut3, dut4]):
            break
        # time.sleep(delay)

    assert ref is not None, f"Reference device {ref_class.__name__} not found"

    return ref, dut1, dut2, dut3, dut4
