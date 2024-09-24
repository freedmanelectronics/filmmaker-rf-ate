import time
from typing import Literal
from serial import Serial


class ArduinoException(Exception):
    pass


class RFATEArduino:
    def __init__(
        self,
        port: str,
        baudrate: int = 57600,
        timeout: float = 0.3,
        eol: Literal["\r\n", "\n", "\r"] = "\r\n",
    ):
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._eol = eol
        self._serial: Serial = None

    def __enter__(self):
        self._serial = Serial(
            port=self._port, baudrate=self._baudrate, timeout=self._timeout
        )
        self._serial.readlines()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._serial.close()

    def write_read(self, msg: str, sleep_time: float = 0.3) -> str:
        time.sleep(sleep_time)
        self._serial.write(bytes(msg + self._eol, "utf-8"))
        response = self._serial.read_until(bytes(self._eol, "utf-8"))

        return response.decode("utf-8").replace(self._eol, "")

    def get_analog(self, channel: Literal[0, 1]):
        response = self.write_read(f"A{channel}")
        ret = None
        for i in range(5):
            try:
                ret = float(response)
            except ValueError:
                response = self._serial.read_until(bytes(self._eol, "utf-8"))
                continue

        if ret:
            return ret
        else:
            raise ArduinoException(
                f"Failed to decode analog from channel {channel}. Response from arduino: `{response}`"
            )

    def get_radio_power(self):
        voltage = self.get_analog(0)
        power = -40 * voltage + 20
        return power

    def set_mode(self, mode: Literal['M', 'Z', 'P']):
        self._serial.write(bytes(f'M{mode}' + self._eol, "utf-8"))
        response = self._serial.read_until(bytes(self._eol, "utf-8"))
        for i in range(5):
            if 'OK' in str(response):
                return
            response = self._serial.read_until(bytes(self._eol, "utf-8"))

        raise ArduinoException(f'Failed to set Arduino mode `{mode}. Response from arduino: `{response}`')


if __name__ == "__main__":
    with RFATEArduino("COM4") as ard:
        res = ard.get_analog(0)
        ard.set_mode('M')
        ard.set_mode('Z')
    print(res)
