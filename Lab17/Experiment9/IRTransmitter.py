

# Test code to check the interfaced seesaw library for interacting with Gamepad QT with PICO
#sends high-precision 8-bit packed data instead of 5 commands.

from machine import I2C, Pin
import seesaw
import time
import ir_tx
import machine
from ir_tx.nec import NEC

# --- Pins 
tx_pin = Pin(19, Pin.OUT, value=0)
device_addr = 0x01
transmitter = NEC(tx_pin)
i2c = I2C(0, scl=Pin(17), sda=Pin(16))
seesaw_device = seesaw.Seesaw(i2c, addr=0x50)

# --- Constants 
BUTTON_A = 5
BUTTON_B = 1
BUTTON_X = 6
BUTTON_Y = 2
BUTTON_START = 16
BUTTON_SELECT = 0
JOYSTICK_X_PIN = 14
JOYSTICK_Y_PIN = 15

BUTTONS_MASK = (1 << BUTTON_X) | (1 << BUTTON_Y) | \
 (1 << BUTTON_A) | (1 << BUTTON_B) | \
 (1 << BUTTON_SELECT) | (1 << BUTTON_START)

# --- Joystick Calibration Constants ---
joystick_center_x = 508
joystick_center_y = 519
joystick_threshold = 50 # Keep the threshold to know when to send data

# --- LED Pins (No changes) ---
LED_1_PIN = 12
LED_2_PIN = 13
LED_3_PIN = 15
LED_4_PIN = 14

led_states = {
    BUTTON_A: False, BUTTON_B: False, BUTTON_X: False, BUTTON_Y: False,
    BUTTON_START: False, BUTTON_SELECT: False
}

def setup_buttons():
    seesaw_device.pin_mode_bulk(BUTTONS_MASK, seesaw_device.INPUT_PULLUP)

def read_buttons():
    return seesaw_device.digital_read_bulk(BUTTONS_MASK)

def set_led(pin, state):
    pin.value(state)

def handle_button_press(button):

    global led_states
    led_states[button] = not led_states[button]
    if button == BUTTON_A:
        set_led(Pin(LED_1_PIN, Pin.OUT), led_states[button])
    elif button == BUTTON_B:
        set_led(Pin(LED_2_PIN, Pin.OUT), led_states[button])
    elif button == BUTTON_X:
        set_led(Pin(LED_3_PIN, Pin.OUT), led_states[button])
    elif button == BUTTON_Y:
        set_led(Pin(LED_4_PIN, Pin.OUT), led_states[button])
    print("Button", button, "is", "pressed" if led_states[button] else "released")

# ==================================
#         MAIN PROGRAM LOOP
# ==================================
def main():
    global last_buttons
    setup_buttons()
    
    last_buttons = 0
    last_x, last_y = seesaw_device.analog_read(JOYSTICK_X_PIN), seesaw_device.analog_read(JOYSTICK_Y_PIN)
    
    # We need a variable to track the last command sent to avoid flooding the IR
    last_command_sent = -1 
    
    # Center command: X=7, Y=7 (approx 512)
    # 7 << 4 = 112. 112 | 7 = 119.
    CENTER_COMMAND = 0b01110111 # (119)
    
    # We will send a "stop" command if the joystick is centered
    transmitter.transmit(device_addr, CENTER_COMMAND)

    while True:
        # --- Button Reading (No changes) ---
        current_buttons = read_buttons()
        for button in led_states:
            if current_buttons & (1 << button) and not last_buttons & (1 << button):
                handle_button_press(button)
        last_buttons = current_buttons
        
        # --- Read Joystick ---
        current_x = seesaw_device.analog_read(JOYSTICK_X_PIN)
        current_y = seesaw_device.analog_read(JOYSTICK_Y_PIN)

        # --- Check for Significant Change ---
        if abs(current_x - last_x) > joystick_threshold or abs(current_y - last_y) > joystick_threshold:
            
            # Update last known position
            last_x, last_y = current_x, current_y

            # Compress 10-bit (0-1023) to 4-bit (0-15)
            # We use 1024 as the divisor for a clean range
            y_quantized = int((current_y / 1024) * 16)
            x_quantized = int((current_x / 1024) * 16)
            
            # Clamp values just in case
            if y_quantized > 15: y_quantized = 15
            if x_quantized > 15: x_quantized = 15

            # Combine into one 8-bit command [YYYYXXXX]
            # Shift Y 4 bits to the left, then OR it with X
            command_to_send = (y_quantized << 4) | x_quantized
            
            # 3. TRANSMIT: Only send if it's a new command
            if (command_to_send != last_command_sent):
                transmitter.transmit(device_addr, command_to_send)
                last_command_sent = command_to_send
                if(command_to_send == CENTER_COMMAND): # Center command
                    transmitter.transmit(device_addr, command_to_send)
                    last_command_sent = command_to_send
                    transmitter.transmit(device_addr, command_to_send)
                    last_command_sent = command_to_send #redudant center commands
                
                print(f"X: {current_x}, Y: {current_y} -> CMD: 0x{command_to_send:02X} [Y:{y_quantized}, X:{x_quantized}]")

        time.sleep(0.05) # Poll at 20Hz

if __name__ == "__main__":
    main()
