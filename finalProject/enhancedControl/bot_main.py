# robot_main.py
#
# EDITED: Now includes a fail-safe timeout.
# If no IR command is received for 300ms, the motors will stop.

import time
from machine import Pin
import motor_control  # Import our new module

# --- IR Receiver Setup ---
from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error

IR_PIN = 18
g_ir_command = 0b01110111  # Default "stop" command
g_last_ir_time = time.ticks_ms() # NEW: Timestamp for the last IR command
IR_TIMEOUT_MS = 300 # NEW: Stop motors if no command for 300ms

def ir_callback(data, addr, _):
    """IR Interrupt: Called when any NEC command is received."""
    global g_ir_command, g_last_ir_time
    g_ir_command = data
    g_last_ir_time = time.ticks_ms() # NEW: Update the timestamp
    # print(f"IR Command Received: 0x{data:02X}") # Optional: for debugging

# --- RF Receiver Setup (No changes) ---
RF_PIN_NUMS = [7, 6, 5, 4]
rf_pins = [Pin(p, Pin.IN) for p in RF_PIN_NUMS]

# --- Mode Switch Setup (No changes) ---
SWITCH_PIN = 10
switch = Pin(SWITCH_PIN, Pin.IN, Pin.PULL_DOWN) 

# --- Joystick Mapping Constants (No changes) ---
JOYSTICK_DEADZONE = 0.1 

# ==================================
# MAPPING LOGIC
# ==================================

def decode_ir_command(command):
    """(No changes to this function)"""
    y_quantized = (command >> 4) & 0x0F
    x_quantized = command & 0x0F

    y_norm = (y_quantized - 7.5) / 7.5
    x_norm = (x_quantized - 7.5) / 7.5

    if abs(x_norm) < JOYSTICK_DEADZONE: x_norm = 0.0
    if abs(y_norm) < JOYSTICK_DEADZONE: y_norm = 0.0

    return (x_norm, y_norm)

def map_rf_to_speeds(rf_vals):
    """
    (Using your new RF logic)
    """
    left_speed = 0.0
    right_speed = 0.0
    
    if rf_vals[0] == 1: 
        left_speed = 0.3
        right_speed = 0.3 #straight forward
    elif rf_vals[1] == 1:
        left_speed = -0.3
        right_speed = -0.3 #straight backward
    elif rf_vals[2] == 1:
        left_speed = -0.3
        right_speed = 0.3 #turn left
    elif rf_vals[3] == 1:
        left_speed = 0.3
        right_speed = -0.3 #turn right
        
    return (left_speed, right_speed)

def read_rf_channels():
    """(No changes)"""
    return [rf_pins[i].value() for i in range(len(rf_pins))]

# ==================================
#         MAIN PROGRAM
# ==================================

motor_control.init()
ir_receiver = NEC_8(Pin(IR_PIN, Pin.IN, Pin.PULL_UP), callback=ir_callback)
ir_receiver.error_function(print_error)

print("Robot main loop starting...")
print("Switch=0 (RF), Switch=1 (IR)")

try:
    while True:
        left = 0.0
        right = 0.0
        current_time = time.ticks_ms()
        
        if switch.value() == 0:
            # --- RF Mode ---
            rf_values = read_rf_channels()
            (left, right) = map_rf_to_speeds(rf_values)
            
            # Reset IR command to "stop" when not in IR mode
            g_ir_command = 0b01110111 

        else:
            # --- IR Mode ---
            
            # NEW: Check for IR Timeout
            time_since_last_cmd = time.ticks_diff(current_time, g_last_ir_time)
            
            if time_since_last_cmd > IR_TIMEOUT_MS:
                # Signal is lost! Stop the motors.
                left = 0.0
                right = 0.0
                g_ir_command = 0b01110111 # Reset to center
            else:
                # Signal is active, run the normal logic
                
                # 1. Decode the 8-bit command to get normalized X and Y
                (x_norm, y_norm) = decode_ir_command(g_ir_command)

                # 2. Map normalized values to motor speeds
                throttle = -y_norm 
                steer = x_norm
                
                # 3. Mix for differential drive
                left_speed = throttle + steer
                right_speed = throttle - steer
                
                # 4. Clip values to be safe
                left = max(-0.3, min(0.3, left_speed))
                right = max(-0.3, min(0.3, right_speed))
                
                # (Removed the redundant left = left_speed)

        # --- Send final commands to motors ---
        motor_control.set_motor_speeds(left, right)
        
        time.sleep(0.02) # Main loop polls at 50Hz

except KeyboardInterrupt:
    print("Stopping.")
    motor_control.stop_all()
