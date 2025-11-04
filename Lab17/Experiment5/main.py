import math, time
import machine
# load the MicroPython pulse-width-modulation module for driving hardware
from machine import PWM

from machine import Pin

time.sleep(1) 


pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT) # Initialize GP14 as an OUTPUT
ain2_en = PWM(13, freq = pwm_rate, duty_u16 = 0)

bin1_ph = Pin(14, Pin.OUT) # Initialize GP14 as an OUTPUT
bin2_en = PWM(15, freq = pwm_rate, duty_u16 = 0)


pwm = min(max(int(2**16 * abs(1)), 0), 20000)

while True:
   # print("Motor A -- Forward") # Print to REPL
    ain1_ph.low()
    ain2_en.duty_u16(pwm)
   # time.sleep(2)
    #print("Motor OFF") # Print to REPL
    #ain1_ph.low()
   # ain2_en.duty_u16(0)
   # time.sleep(2)
   # print("Motor B -- Backward") # Print to REPL
    bin1_ph.high()
    bin2_en.duty_u16(pwm)
   # time.sleep(2)
  #  print("Motor OFF") # Print to REPL
    #bin1_ph.low()
   # bin2_en.duty_u16(0)
    #time.sleep(2)
