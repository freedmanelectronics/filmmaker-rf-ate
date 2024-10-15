from kivy.app import App
from rode.devices.wireless.bases.wireless_device_base import WirelessDeviceBase

from filmmaker_rf_ate.gui.custom_widgets import RootLayout


class Filmmaker2RFApp(App):
    # Build
    # --------
    def __init__(
        self, ref_class: type(WirelessDeviceBase), dut_class: type(WirelessDeviceBase)
    ):
        self._ref_class = ref_class
        self._dut_class = dut_class
        super().__init__()

    def build(self):
        return RootLayout(self._ref_class, self._dut_class)


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG

    Filmmaker2RFApp(CONFIG.device_classes.ref, CONFIG.device_classes.dut).run()
