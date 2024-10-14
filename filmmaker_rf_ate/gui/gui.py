from kivy.app import App
from filmmaker_rf_ate.gui.custom_widgets import RootLayout


class Filmmaker2RFApp(App):
    # Build
    # --------

    def build(self):
        return RootLayout()


if __name__ == "__main__":
    Filmmaker2RFApp().run()
