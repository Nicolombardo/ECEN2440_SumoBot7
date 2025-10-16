import math, time
import machine


from machine import PWM

from machine import Pin

led1 = Pin(16, Pin.OUT)
led2 = Pin(17, Pin.OUT)
led3 = Pin(18, Pin.OUT)

while True:
    led1.toggle()
    led2.toggle()
    led3.toggle()
    time.sleep(2)