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

switch = Pin(10, Pin.IN, Pin.PULL_DOWN)

RF1_pin = Pin(15, Pin.IN)
RF2_pin = Pin(14, Pin.IN)
RF3_pin = Pin(13, Pin.IN)
RF4_pin = Pin(12, Pin.IN)

def ir_callback(data, addr, _):
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")
    global command
    if switch.value() == 1:
        command = data
    else:
        command = 0

def RF_check():
    global command
    if switch.value() == 0:
        if RF1_pin.value() == 1:
            command = 0x01
        if RF2_pin.value() == 1:
            command = 0x02
        if RF3_pin.value() == 1:
            command = 0x03
        if RF4_pin.value() == 1:
            command = 0x04
        if RF1_pin.value() == 0 and RF2_pin.value() == 0 and RF3_pin.value() == 0 and RF4_pin.value() == 0:
            command = 0x05

ir_pin = Pin(20, Pin.IN, Pin.PULL_UP) 

ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error)

ledRed = Pin(16, Pin.OUT)
ledGreen = Pin(17, Pin.OUT)
ledBlue = Pin(18, Pin.OUT)
ledYellow = Pin(19, Pin.OUT)


while True:
    RF_check()
    if command == 0x01:
        ledRed.high()
    if command == 0x02:
        ledGreen.high()
    if command == 0x03:
        ledBlue.high()
    if command == 0x04:
        ledYellow.high() 
    if command == 0x05:
        ledGreen.low()
        ledRed.low()
        ledBlue.low()
        ledYellow.low()   
