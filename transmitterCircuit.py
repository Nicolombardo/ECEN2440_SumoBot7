import ir_tx
import time
import machine
from ir_tx.nec import NEC
from machine import Pin
tx_pin = Pin(17,Pin.OUT,value=0)
device_addr = 0x01
transmitter = NEC(tx_pin) #initalize transmitter
commands = [0x01,0x02,0x03,0x04,0x05,0x06,0x03,0x04] #command setup (tests all directions)
#01 forward right, 02 forward left, 03 stop right, 04 stop left, 05 backwards right
#06 backwards left

if __name__ == "__main__": 
    while True: #loop to transmit the commands
        for command in commands:
            transmitter.transmit(device_addr,command) #send the signal
            print("COMMANDS",hex(command),"TRANSMITTED.") #print to repl
    

            time.sleep(2) #add a buffer time in between commands
