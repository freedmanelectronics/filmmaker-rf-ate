from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from filmmaker_rf_ate.gui.graphics.colours import hex_to_kivy, PRIMARY, SUCCESS, ERROR


class RootLayout(BoxLayout):
    def scan(self):
        self.ids.dut_layout.dut_widgets[0].set_color_fail()

    def start_test(self):
        self.ids.dut_layout.dut_widgets[0].set_color_pass()


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
