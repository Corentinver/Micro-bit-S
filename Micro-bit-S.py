from microbit import *
import radio


# On initialise la communication Radio
radio.on()
radio.config(length=251)
radio.config(channel=45)
radio.config(address=0x86245977)

# On initialise la communication UART
uart.init(baudrate=115200, bits=2048)

def request_connection(request): 
    display.set_pixel(3, 3, 5)
    radio.send(str(request))
    return

while True:
    # On attend un message du serveur
    UARTmessage = uart.readline()

    try:
        request = eval(UARTmessage)
    except:
        continue

    request_connection(request)
