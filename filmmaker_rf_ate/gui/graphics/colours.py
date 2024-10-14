from collections import namedtuple

NEUTRAL = 0x3D4451
PRIMARY = 0x2D6AED
SECONDARY = 0x2EE898
ACCENT = 0xFFA217
COLOR = 0x2D6AED
INFO = 0x17A2B8
SUCCESS = 0x64BC4F
WARNING = 0xFFC107
ERROR = 0xDC3545

BASE_100 = 0x000000
BASE_200 = 0x141414
BASE_300 = 0x262626

RGBColor = namedtuple("RGBColor", ("red", "green", "blue"))
KivyColor = namedtuple("KivyColor", ("red", "green", "blue", "alpha"))


def hex_to_rgb(hex_color: int) -> RGBColor:
    b = hex_color & 255
    g = (hex_color >> 8) & 255
    r = (hex_color >> 16) & 255

    return RGBColor(r, g, b)


def rgb_to_kivy(rgb: RGBColor, alpha=1) -> KivyColor:
    return KivyColor(rgb.red / 255, rgb.green / 255, rgb.blue / 255, alpha)


def hex_to_kivy(hex_color: int, alpha=1) -> KivyColor:
    return KivyColor(*rgb_to_kivy(hex_to_rgb(hex_color), alpha))
