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

pwm = min(max(int(2**16 * abs(1)), 0), 20000)

switch = Pin(10, Pin.IN, Pin.PULL_DOWN)

RF1_pin = Pin(7, Pin.IN)
RF2_pin = Pin(6, Pin.IN)
RF3_pin = Pin(5, Pin.IN)
RF4_pin = Pin(4, Pin.IN)

pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT) # Initialize GP14 as an OUTPUT
ain2_en = PWM(13, freq = pwm_rate, duty_u16 = 0)

bin1_ph = Pin(14, Pin.OUT)
bin2_en = PWM(15, freq = pwm_rate, duty_u16 = 0)

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
        if RF1_pin.value() == 1 and RF2_pin.value() == 1:
            command = 0x06
        elif RF3_pin.value() == 1 and RF4_pin.value() == 1:
            command = 0x07
        elif RF1_pin.value() == 1 and RF4_pin.value() == 1:
            command = 0x08
        elif RF2_pin.value() == 1 and RF3_pin.value() == 1:
            command = 0x09
        elif RF1_pin.value()  == 1:
            command = 0x01
        elif RF2_pin.value() == 1:
            command = 0x02
        elif RF3_pin.value() == 1:
            command = 0x03
        elif RF4_pin.value() == 1:
            command = 0x04
        elif RF1_pin.value() == 0 and RF2_pin.value() == 0 and RF3_pin.value() == 0 and RF4_pin.value() == 0:
            command = 0x05
        

ir_pin = Pin(18, Pin.IN, Pin.PULL_UP) 

ir_receiver = NEC_8(ir_pin, callback=ir_callback)
ir_receiver.error_function(print_error)



while True:
    RF_check()
    if command == 0x01:   #forward right
        bin1_ph.low()
        bin2_en.duty_u16(pwm)
    elif command == 0x02:   #forward left
        ain1_ph.high()
        ain2_en.duty_u16(pwm)
    elif command == 0x03:   #backward right
        bin1_ph.high()
        bin2_en.duty_u16(pwm)
    elif command == 0x04:   #backward left
        ain1_ph.low()
        ain2_en.duty_u16(pwm)
    elif command == 0x05:  #stop
        bin1_ph.low()
        bin2_en.duty_u16(0)
        ain1_ph.low()
        ain2_en.duty_u16(0)
    elif command == 0x06:    #forward both 
        ain1_ph.high()
        ain2_en.duty_u16(pwm)
        bin1_ph.low()
        bin2_en.duty_u16(pwm)
    elif command == 0x07:     #backward both
        ain1_ph.low()
        ain2_en.duty_u16(pwm)
        bin1_ph.high()
        bin2_en.duty_u16(pwm)
    elif command == 0x08:      #left spin
        bin1_ph.low()
        bin2_en.duty_u16(pwm)
        ain1_ph.low()
        ain2_en.duty_u16(pwm)
    elif command == 0x09:      #right spin
        bin1_ph.high()
        bin2_en.duty_u16(pwm)
        ain1_ph.high()
        ain2_en.duty_u16(pwm)

