from machine import Pin
import time

GP3 = Pin(3, Pin.OUT)

while True:
    GP3.high()
    time.sleep(1)
    GP3.low()
    time.sleep(1)
