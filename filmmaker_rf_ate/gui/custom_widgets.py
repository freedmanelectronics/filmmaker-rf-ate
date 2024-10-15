import threading

from functional_test_core.device_test.observer import Observer, Observable, Message
from functional_test_core.models import DeviceInfo
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from kivy.uix.label import Label
from rode.devices.wireless.bases.wireless_device_base import WirelessDeviceBase

from filmmaker_rf_ate.config import Config
from filmmaker_rf_ate.gui.graphics.colours import hex_to_kivy, PRIMARY, SUCCESS, ERROR
from filmmaker_rf_ate.get_devices import get_devices
from filmmaker_rf_ate.tests.test_factory import mock_test_factory, test_factory


class DutWidgetObserver(Observer):
    def __init__(self, dut_widget: "DUTWidget", log_label: Label):
        super().__init__()
        self._dut_widget = dut_widget
        self._log_label = log_label

    @property
    def dut_widget(self) -> "DUTWidget":
        return self._dut_widget

    @dut_widget.setter
    def dut_widget(self, value: "DUTWidget"):
        self._dut_widget = value

    def update(self, observable: Observable, message: Message, *args, **kwargs):
        self._log_label.text = message.content

        if message.status == "running":
            self._dut_widget.set_color_running()
        elif message.status == "pass":
            self._dut_widget.set_color_pass()
        elif message.status == "fail":
            self._dut_widget.set_color_fail()


class RootLayout(BoxLayout):
    def __init__(
        self,
        config: Config,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.ref: DeviceInfo | None = None
        self._test_config = config
        self.duts: list[DeviceInfo | None] = [None, None, None, None]

    def _scan_devices(
        self,
    ) -> tuple[
        DeviceInfo | None,
        DeviceInfo | None,
        DeviceInfo | None,
        DeviceInfo | None,
        DeviceInfo | None,
    ]:
        self.ids.log_label.text = "Scanning for devices..."
        for widget in self.ids.dut_layout.dut_widgets:
            widget.disabled = True

        try:
            ref, *duts = get_devices(self._test_config.device_classes.dut, self._test_config.device_classes.ref, retries=5)
        except AssertionError:
            self.ids.log_label.text = "Reference unit not found! Check connection."
            return None, None, None, None, None

        self.ids.log_label.text = (
            f"{len([dut for dut in duts if dut is not None])} device(s) found!"
        )

        for dut, widget in zip(duts, self.ids.dut_layout.dut_widgets):
            if dut is not None:
                widget.disabled = False
            else:
                widget.disabled = True

        return ref, *duts

    def scan_button_callback(self):
        threading.Thread(target=self._scan_devices).start()

    def start_test(self):
        def _start_test_callback():
            ref, *duts = self._scan_devices()

            if not ref:
                return

            observer = DutWidgetObserver(duts[0], log_label=self.ids.log_label)

            for dut, widget in zip(duts, self.ids.dut_layout.dut_widgets):
                if dut is None:
                    continue

                observer.dut_widget = widget

                test_handler = test_factory(ref, dut, self._test_config)
                test_handler.add_observer(observer)
                test_handler.execute_tests()

        threading.Thread(target=_start_test_callback).start()


class DUTLayout(BoxLayout):
    dut_widgets: list["DUTWidget"] = ListProperty([])

    def disable_board(self, idx: int):
        self.dut_widgets[idx].disabled = True

    def enable_board(self, idx: int):
        self.dut_widgets[idx].disabled = False


# Individual board status layout
class DUTWidget(BoxLayout):
    board_name = StringProperty("DUT")
    color = ListProperty([1, 1, 1, 0.3])
    disabled_color = [1, 1, 1, 0.3]
    enabled_color = [1, 1, 1, 1]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.disabled = True

    def on_disabled(self, instance, value: bool):
        if value:
            self.color = self.disabled_color
        else:
            self.color = self.enabled_color

    def set_color_running(self):
        self.color = hex_to_kivy(PRIMARY)

    def set_color_pass(self):
        self.color = hex_to_kivy(SUCCESS)

    def set_color_fail(self):
        self.color = hex_to_kivy(ERROR)
