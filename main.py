from machine import Pin, Timer
import time

# Configure the button pin (GPIO 14 with internal pull-up resistor)
button = Pin(14, Pin.IN, Pin.PULL_UP)

# Debounce timer
debounce_timer = Timer(0)

def button_pressed(pin):
    # Disable interrupt during debounce to prevent multiple triggers
    button.irq(handler=None)
    
    # Schedule re-enabling after 200ms (debounce period)
    debounce_timer.init(mode=Timer.ONE_SHOT, period=200, callback=reenable_interrupt)
    
    # Your code to execute when button is pressed
    # Add your code here
    print("Button pressed!")
    # Example: send data, read sensors, toggle something, etc.

def reenable_interrupt(timer):
    # Re-enable the interrupt after debounce period
    button.irq(handler=button_pressed, trigger=Pin.IRQ_FALLING)

# Set up interrupt on falling edge (button press)
button.irq(handler=button_pressed, trigger=Pin.IRQ_FALLING)

print("Waiting for button press...")

# Keep the program running
while True:
    # You can add other code here that runs in the main loop
    time.sleep(1)