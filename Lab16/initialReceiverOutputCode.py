from machine import Pin
import time

# Setup 4 RF input pins (use GP numbers)
RF_PINS = [15, 14, 13, 12]
PULL = None  # set to Pin.PULL_UP or Pin.PULL_DOWN if needed later
SIGNAL_NAMES = ["CH1", "CH2", "CH3", "CH4"]

# setup the pins
if PULL is None:
    pins = [Pin(p, Pin.IN) for p in RF_PINS]
else:
    pins = [Pin(p, Pin.IN, PULL) for p in RF_PINS]

def read_raw():
    return [pins[i].value() for i in range(len(pins))] #define the data read from the pins

def main():
    print("Pins initialized:", RF_PINS)
    while True:
        vals = read_raw() #read the direct values
        print("RAW:", " ".join(f"{n}:{v}" for n, v in zip(SIGNAL_NAMES, vals))) #read out the raw data and print
        time.sleep(0.5) #give a delay

if __name__ == "__main__":
    main()
