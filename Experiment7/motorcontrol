#   Pico pin GP13   -> AIN2
#   Pico pin GP12   -> AIN1
#   any Pico GND    -> GND

import ir_rx
import math, time
import machine
# load the MicroPython pulse-width-modulation module for driving hardware
from machine import PWM

from machine import Pin

from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error # for debugging


time.sleep(1) # Wait for USB to become ready

command = 0

def ir_callback(data, addr, _):
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")
    global command
    command = data

ir_pin = Pin(19, Pin.IN, Pin.PULL_UP) # Adjust the pin number based on your 


ir_receiver = NEC_8(ir_pin, callback=ir_callback)
# Optional: Use the print_error function for debugging
ir_receiver.error_function(print_error)


pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT) # Initialize GP14 as an OUTPUT
ain2_en = PWM(13, freq = pwm_rate, duty_u16 = 0)

bin1_ph = Pin(14, Pin.OUT)
bin2_en = PWM(15, freq = pwm_rate, duty_u16 = 0)



pwm = min(max(int(2**16 * abs(1)), 0), 20000)

def forwardLeft():
    bin1_ph.low()
    bin2_en.duty_u16(pwm)
    time.sleep(1)

def forwardRight():
    ain1_ph.high()
    ain2_en.duty_u16(pwm)
    time.sleep(1)

def backwardLeft():
    bin1_ph.high()
    bin2_en.duty_u16(pwm)
    time.sleep(1)

def backwardRight():
    ain1_ph.low()
    ain2_en.duty_u16(pwm)
    time.sleep(1)

def stopLeft():
    bin1_ph.low()
    bin2_en.duty_u16(0)
    time.sleep(1)

def stopRight():
    ain1_ph.low()
    ain2_en.duty_u16(0)
    time.sleep(1)

forwardRight()
forwardLeft()
while True:

    if command == 0x04:
        forwardRight()
    if command == 0x03:
        forwardLeft()
    if command == 0x01:
        forwardLeft()
        forwardRight()
    if command == 0x05:
        stopLeft()
        stopRight()
    if command == 0x02:
        backwardRight()
        backwardLeft()
