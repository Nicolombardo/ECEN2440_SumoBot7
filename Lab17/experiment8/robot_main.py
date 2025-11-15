# robot_main.py
#
# 
# decodes the 8-bit [YYYYXXXX] command
# and maps it to precise motor speeds.

import time
from machine import Pin
import motor_control  # Import our new module

# --- IR Receiver Setup ---
from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error

IR_PIN = 18
# We now store 0b01110111 (Center X=7, Y=7) as the default "stop"
g_ir_command = 0b01110111  

def ir_callback(data, addr, _):
    """IR Interrupt: Called when any NEC command is received."""
    global g_ir_command
    g_ir_command = data
    # print(f"IR Command Received: 0x{data:02X}") # Optional: for debugging

# --- RF Receiver Setup (No changes) ---
RF_PIN_NUMS = [4, 5, 6, 7]
rf_pins = [Pin(p, Pin.IN) for p in RF_PIN_NUMS]

# --- Mode Switch Setup (No changes) ---
SWITCH_PIN = 10
switch = Pin(SWITCH_PIN, Pin.IN, Pin.PULL_DOWN) 

# --- Joystick Mapping Constants ---
JOYSTICK_DEADZONE = 0.1 # 10% deadzone (0.1 / 7.5 = ~0.01)

# ==================================
# MAPPING LOGIC
# ==================================

def decode_ir_command(command):
    """
    Decodes the 8-bit [YYYYXXXX] command into normalized
    throttle and steer values (-1.0 to 1.0).
    """
    # 1. UNPACK: Isolate the Y and X values
    # g_ir_command = 0bYYYYXXXX
    
    # y_quantized = (0bYYYYXXXX >> 4) & 0x0F = 0b0000YYYY
    y_quantized = (command >> 4) & 0x0F
    
    # x_quantized = 0bYYYYXXXX & 0x0F = 0b0000XXXX
    x_quantized = command & 0x0F

    # 2. Convert 4-bit (0-15) to normalized float (-1.0 to 1.0)
    # The center point of 0-15 is 7.5
    # (0.0 - 7.5) / 7.5 = -1.0
    # (7.5 - 7.5) / 7.5 = 0.0
    # (15.0 - 7.5) / 7.5 = 1.0
    y_norm = (y_quantized - 7.5) / 7.5
    x_norm = (x_quantized - 7.5) / 7.5

    # 3. APPLY DEADZONE:
    # (This check is cheap and safer than relying on the transmitter)
    if abs(x_norm) < JOYSTICK_DEADZONE: x_norm = 0.0
    if abs(y_norm) < JOYSTICK_DEADZONE: y_norm = 0.0

    return (x_norm, y_norm)

def map_rf_to_speeds(rf_vals):
    """
    (No changes)
    Translates the 4-button RF input (tank style) into
    motor speeds (-1.0 to 1.0).
    """
    left_speed = 0.0
    right_speed = 0.0
    
    if rf_vals[0] == 1: 
        left_speed = 0.1
        right_speed = 0.1 #straight forward
        ##print("forward")
        ##time.sleep(0.1)
    elif rf_vals[1] == 1:
        left_speed = -0.1
        right_speed = -0.1 #straight backward
    elif rf_vals[2] == 1:
        left_speed = 0.0
        right_speed = 0.2 #turn left
    elif rf_vals[3] == 1:
        left_speed = 0.2
        right_speed = -0.0 #turn right

    #tank style control commented out
    ##if rf_vals[0] == 1: left_speed = 1.0
    ##elif rf_vals[2] == 1: left_speed = -1.0
        
    ##if rf_vals[1] == 1: right_speed = 1.0
    ##elif rf_vals[3] == 1: right_speed = -1.0
        
    return (left_speed, right_speed)

def read_rf_channels():
    """Reads the raw RF pin values."""
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
        
        if True:
            # --- RF Mode ---
            rf_values = read_rf_channels()
            (left, right) = map_rf_to_speeds(rf_values)
            
            # Reset IR command to "stop" when not in IR mode
            g_ir_command = 0b01110111 

        else:
            # --- IR Mode ---
            
            # 1. Decode the 8-bit command to get normalized X and Y
            (x_norm, y_norm) = decode_ir_command(g_ir_command)

            # 2. Map normalized values to motor speeds
            # We invert y_norm (throttle) because on the joystick,
            # 0 (UP) becomes -1.0, and we want UP to be positive throttle.
            throttle = -y_norm 
            steer = x_norm
            
            # 3. Mix for differential drive
            left_speed = throttle + steer
            right_speed = throttle - steer
            
            # 4. Clip values to be safe
            left_speed = max(-0.3, min(0.3, left_speed))
            right_speed = max(-0.3, min(0.3, right_speed))

            left = left_speed
            right = right_speed

        # --- Send final commands to motors ---
        motor_control.set_motor_speeds(left, right)
        
        time.sleep(0.02) # Poll at 50Hz

except KeyboardInterrupt:
    print("Stopping.")
    motor_control.stop_all()
