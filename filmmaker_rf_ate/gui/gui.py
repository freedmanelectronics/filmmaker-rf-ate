from kivy.app import App
from rode.devices.wireless.bases.wireless_device_base import WirelessDeviceBase
from filmmaker_rf_ate.config import Config

from filmmaker_rf_ate.gui.custom_widgets import RootLayout


class Filmmaker2RFApp(App):
    # Build
    # --------
    def __init__(self, config: Config):
        self._test_config = config
        super().__init__()

    def build(self):
        return RootLayout(self._test_config)


if __name__ == "__main__":
    from filmmaker_rf_ate.config import CONFIG

    Filmmaker2RFApp(CONFIG).run()
