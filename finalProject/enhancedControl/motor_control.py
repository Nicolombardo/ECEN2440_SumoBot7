# motor_control.py
# A module for controlling a 2-wheel robot with a Phase/Enable motor driver.
# Assumes:
# Left Motor:  GP14 (Phase), GP15 (Enable/PWM)
# Right Motor: GP12 (Phase), GP13 (Enable/PWM)

from machine import Pin, PWM

# --- Constants ---
MAX_PWM_DUTY = 65535  # The max value for duty_u16
PWM_FREQ = 1000      #placeholder might need later

# --- Left Motor Pins ---
# We name them based on the *action* (forward/backward)
# PLACEHOLDER, MIGHT NEED TO CHANGE LATER
LEFT_PHASE_PIN = 14 
LEFT_ENABLE_PIN = 15 
LEFT_FWD = 0  # 0 = low()
LEFT_REV = 1  # 1 = high()

# --- Right Motor Pins ---

RIGHT_PHASE_PIN = 12 
RIGHT_ENABLE_PIN = 13 
RIGHT_FWD = 1 # 1 = high()
RIGHT_REV = 0 # 0 = low()

# --- Private Pin Objects ---
_left_ph = None
_left_en = None
_right_ph = None
_right_en = None

def init():
    """Initializes all motor pins."""
    global _left_ph, _left_en, _right_ph, _right_en
    
    # --- Left Motor Init ---
    _left_ph = Pin(LEFT_PHASE_PIN, Pin.OUT)
    _left_en = PWM(Pin(LEFT_ENABLE_PIN))
    _left_en.freq(PWM_FREQ)
    _left_ph.value(LEFT_FWD)
    _left_en.duty_u16(0)
    
    # --- Right Motor Init ---
    _right_ph = Pin(RIGHT_PHASE_PIN, Pin.OUT)
    _right_en = PWM(Pin(RIGHT_ENABLE_PIN))
    _right_en.freq(PWM_FREQ)
    _right_ph.value(RIGHT_FWD)
    _right_en.duty_u16(0)
    
    print("Motor control initialized.")

def _set_motor(phase_pin, enable_pwm, fwd_val, rev_val, speed):
    """Internal helper to control a single motor."""
    
    # Clamp speed to -1.0 .. 1.0
    if speed > 1.0: speed = 1.0
    if speed < -1.0: speed = -1.0
    
    if speed > 0.01:
        # --- Forward ---
        phase_pin.value(fwd_val)
        duty = int(speed * MAX_PWM_DUTY)
        enable_pwm.duty_u16(duty)
    elif speed < -0.01:
        # --- Backward ---
        phase_pin.value(rev_val)
        duty = int(abs(speed) * MAX_PWM_DUTY)
        enable_pwm.duty_u16(duty)
    else:
        # --- Stop ---
        enable_pwm.duty_u16(0)

def set_motor_speeds(left_speed, right_speed):
    """
    Sets the speed for both motors.
    :param left_speed: float from -1.0 (full reverse) to 1.0 (full forward)
    :param right_speed: float from -1.0 (full reverse) to 1.0 (full forward)
    """
    if _left_ph is None:
        print("Error: Motors not initialized. Call motor_control.init()")
        return
        
    _set_motor(_left_ph, _left_en, LEFT_FWD, LEFT_REV, left_speed)
    _set_motor(_right_ph, _right_en, RIGHT_FWD, RIGHT_REV, right_speed)

def stop_all():
    """Stops both motors."""
    set_motor_speeds(0.0, 0.0)
