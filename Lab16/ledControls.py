from machine import Pin
import time

# Setup 4 RF input pins (use GP numbers)
RF_PINS = [15, 14, 13, 12]
PULL = None  # set to Pin.PULL_UP or Pin.PULL_DOWN if needed later
SIGNAL_NAMES = ["CH1", "CH2", "CH3", "CH4"]

# LEDs mapped to channels: CH1 -> GP16, CH2 -> GP17, CH3 -> GP18, CH4 -> GP19
LED_PINS = [16, 17, 18, 19]

# setup the input pins
if PULL is None:
    pins = [Pin(p, Pin.IN) for p in RF_PINS]
else:
    pins = [Pin(p, Pin.IN, PULL) for p in RF_PINS]

# setup the LED output pins
leds = [Pin(p, Pin.OUT) for p in LED_PINS]
for led in leds:
    led.value(0)  # start with LEDs off

def read_raw():
    return [pins[i].value() for i in range(len(pins))]  # read the data from the pins

def main():
    print("Pins initialized - inputs:", RF_PINS, "leds:", LED_PINS)
    while True:
        vals = read_raw()  # read the direct values
        print("RAW:", " ".join(f"{n}:{v}" for n, v in zip(SIGNAL_NAMES, vals)))  # print raw values
        # drive LEDs to match channel states (1 -> LED on, 0 -> LED off)
        for i, v in enumerate(vals):
            leds[i].value(v)
        time.sleep(0.1)  # poll delay

if __name__ == "__main__":
    main()
