# robot_main.py
# The main code for the robot's Pico.
# This file reads from controllers and uses motor_control.py to move.

import time
from machine import Pin
import motor_control  # Import our new module

# --- RF Receiver Setup
RF_PINS = [15, 14, 13, 12]
rf_pins = [Pin(p, Pin.IN) for p in RF_PINS]
SIGNAL_NAMES = ["CH1", "CH2", "CH3", "CH4"] # L-Fwd, L-Rev, R-Fwd, R-Rev

# --- IR Receiver Setup (from your ir_receiver.py script) ---
# IR SETUP NOT DONE

# --- Joystick Mapping Constants ---
JOYSTICK_CENTER_X = 512.0
JOYSTICK_CENTER_Y = 512.0 # Using 512 as a clean average
JOYSTICK_RANGE = 512.0
JOYSTICK_DEADZONE = 0.1 # 10% deadzone

def map_joystick_to_speeds(x, y):
    """
    Translates raw X/Y (0-1023) joystick values into two motor speeds (-1.0 to 1.0) for skid steering.
    """
    # Normalize values from 0-1023 to -1.0 to 1.0 and then subtract center and divide by range
    x_norm = (x - JOYSTICK_CENTER_X) / JOYSTICK_RANGE
    y_norm = (y - JOYSTICK_CENTER_Y) / JOYSTICK_RANGE
    
    # Apply a "dead zone" to prevent drift when joystick is centered
    if abs(x_norm) < JOYSTICK_DEADZONE:
        x_norm = 0.0
    if abs(y_norm) < JOYSTICK_DEADZONE:
        y_norm = 0.0
    # Map to motor speeds (Arcade/Differential Drive)
    # y_norm is "throttle" (forward/back)
    # x_norm is "steer" (left/right)

    # invert y_norm because 0 is on a joystick, which would translate to forward
    throttle = -y_norm
    steer = x_norm
    
    left_speed = throttle + steer
    right_speed = throttle - steer
    
    # clip the values to ensure they are between -1.0 and 1.0 
    left_speed = max(-1.0, min(1.0, left_speed))
    right_speed = max(-1.0, min(1.0, right_speed))
    
    return (left_speed, right_speed)

def map_rf_to_speeds(rf_vals):
    """
    Translates the 4-button RF input (tank style) into
    motor speeds (-1.0 to 1.0).
    CH1: Left Fwd
    CH2: Left Rev
    CH3: Right Fwd
    CH4: Right Rev
    """
    left_speed = 0.0
    right_speed = 0.0
    
    # --- Left Motor ---
    if rf_vals[0] == 1: # CH1
        left_speed = 1.0
    elif rf_vals[1] == 1: # CH2
        left_speed = -1.0
        
    # --- Right Motor ---
    if rf_vals[2] == 1: # CH3
        right_speed = 1.0
    elif rf_vals[3] == 1: # CH4
        right_speed = -1.0
        
    return (left_speed, right_speed)

def read_rf_channels():
    """Reads the raw RF pin values."""
    return [rf_pins[i].value() for i in range(len(rf_pins))]

# ==================================
#         MAIN PROGRAM LOOP
# ==================================

# 1. Initialize our motor controller
motor_control.init()

# 2. Decide which controller is active
#    assume RF for now, EDIT LATER
#  
ACTIVE_CONTROLLER = "RF" # Can be "RF" or "JOYSTICK"

print("Robot main loop starting...")

try:
    while True:
        left = 0.0
        right = 0.0
        
        if ACTIVE_CONTROLLER == "RF":
            # --- Get data from RF controller ---
            rf_values = read_rf_channels()
            (left, right) = map_rf_to_speeds(rf_values)
            
            # Optional: Print for debugging
            # print(f"RF: {rf_values} -> L:{left:.2f}, R:{right:.2f}")

        elif ACTIVE_CONTROLLER == "JOYSTICK":
            # --- Get data from IR controller ---
            #
            # THIS IS NOT FINISHED YET, PART NEED TO FIX
            # We need to get the *actual* x, y values here,
            # not just the 0x01 command from earlier
            #
            # Example (once we fix the transmitter):
            # (x, y) = get_joystick_data_from_ir() 
            # (left, right) = map_joystick_to_speeds(x, y)
            
            # For now, just test the map function:
            # Test: Full forward
            (left, right) = map_joystick_to_speeds(512, 0) 
            
            
        # --- Send final commands to motors ---
        motor_control.set_motor_speeds(left, right)
        
        time.sleep(0.02) # Poll at 50Hz

except KeyboardInterrupt:
    print("Stopping.")
    motor_control.stop_all()
